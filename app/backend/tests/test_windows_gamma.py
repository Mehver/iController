# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

import os
from unittest.mock import Mock

import pytest


BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..")


@pytest.fixture(autouse=True)
def backend_on_path(monkeypatch):
    monkeypatch.syspath_prepend(BACKEND_DIR)


def make_baseline():
    channel = tuple(index * 257 for index in range(256))
    return (channel, channel, channel)


class FakeGammaAPI:
    def __init__(self, sources=(r"\\.\DISPLAY1",), failures=()):
        self.sources = list(sources)
        self.failures = set(failures)
        self.baseline = make_baseline()
        self.get_calls = []
        self.set_calls = []

    def enumerate_display_sources(self):
        return self.sources

    def get_gamma_ramp(self, source):
        self.get_calls.append(source)
        if source in self.failures:
            raise RuntimeError("read failed")
        return self.baseline

    def set_gamma_ramp(self, source, ramp):
        self.set_calls.append((source, ramp))
        if source in self.failures:
            raise RuntimeError("write failed")


@pytest.fixture
def gamma(monkeypatch):
    from HostCore.brightness_controller import windows_gamma

    adapter = windows_gamma.WindowsGammaBrightness
    adapter._api = None
    adapter._baselines = {}
    adapter._modified_sources = set()
    adapter._current_percent = 100
    adapter._atexit_registered = False
    monkeypatch.setattr(windows_gamma.atexit, "register", Mock())
    return windows_gamma, adapter


def test_scaled_ramp_uses_safe_linear_mapping(gamma):
    module, _ = gamma
    baseline = make_baseline()

    assert module._scaled_ramp(baseline, 100) == baseline
    at_zero = module._scaled_ramp(baseline, 0)
    assert at_zero[0][100] == round(baseline[0][100] * 0.5)
    assert module._scaled_ramp(baseline, -20) == at_zero
    assert module._scaled_ramp(baseline, 120) == baseline


def test_baseline_is_captured_once_and_scaling_does_not_compound(gamma):
    module, adapter = gamma
    api = FakeGammaAPI()
    adapter._api = api

    adapter.set_brightness(0)
    adapter.set_brightness(50)

    assert api.get_calls == [r"\\.\DISPLAY1"]
    assert api.set_calls[0][1] == module._scaled_ramp(api.baseline, 0)
    assert api.set_calls[1][1] == module._scaled_ramp(api.baseline, 50)
    assert adapter().get_brightness() == 50


def test_first_get_captures_baseline_returns_100_and_registers_restore_once(gamma):
    module, adapter = gamma
    api = FakeGammaAPI()
    adapter._api = api

    assert adapter.get_brightness() == 100
    assert adapter.get_brightness() == 100

    assert api.get_calls == [r"\\.\DISPLAY1"]
    module.atexit.register.assert_called_once_with(adapter._restore_at_exit)


def test_set_succeeds_when_at_least_one_display_source_succeeds(gamma):
    _, adapter = gamma
    failed = r"\\.\DISPLAY1"
    working = r"\\.\DISPLAY2"
    api = FakeGammaAPI((failed, working))
    adapter._api = api
    original_set = api.set_gamma_ramp

    def selective_set(source, ramp):
        if source == failed:
            api.set_calls.append((source, ramp))
            raise RuntimeError("driver rejected ramp")
        original_set(source, ramp)

    api.set_gamma_ramp = selective_set
    adapter.set_brightness(25)

    assert [call[0] for call in api.set_calls] == [failed, working]
    assert adapter.get_brightness() == 25


def test_set_raises_when_all_display_sources_fail(gamma):
    module, adapter = gamma
    sources = (r"\\.\DISPLAY1", r"\\.\DISPLAY2")
    api = FakeGammaAPI(sources)
    adapter._api = api

    def fail_set(source, ramp):
        api.set_calls.append((source, ramp))
        raise RuntimeError("driver rejected ramp")

    api.set_gamma_ramp = fail_set

    with pytest.raises(module.WindowsGammaError, match="could not be applied"):
        adapter.set_brightness(25)
    assert len(api.set_calls) == 2
    assert adapter._current_percent == 100


def test_restore_uses_original_baseline_and_ignores_restore_failure(gamma):
    _, adapter = gamma
    api = FakeGammaAPI()
    adapter._api = api
    adapter.set_brightness(20)

    adapter.restore()

    assert api.set_calls[-1] == (r"\\.\DISPLAY1", api.baseline)
    assert adapter.get_brightness() == 100
    api.set_gamma_ramp = Mock(side_effect=RuntimeError("display disappeared"))
    adapter._modified_sources.add(r"\\.\DISPLAY1")
    adapter.restore()  # Normal process exit must not be disrupted.


def test_win32_boundary_deletes_dc_after_get_and_set(gamma):
    module, _ = gamma
    user32 = Mock()
    gdi32 = Mock()
    gdi32.CreateDCW.return_value = 123

    def fill_ramp(_dc, ramp_pointer):
        ramp = ramp_pointer._obj
        for channel in range(3):
            for index in range(256):
                ramp[channel][index] = index
        return True

    gdi32.GetDeviceGammaRamp.side_effect = fill_ramp
    gdi32.SetDeviceGammaRamp.return_value = True
    api = module._Win32GammaAPI(user32=user32, gdi32=gdi32)

    ramp = api.get_gamma_ramp(r"\\.\DISPLAY1")
    api.set_gamma_ramp(r"\\.\DISPLAY1", ramp)

    assert gdi32.DeleteDC.call_count == 2


def test_win32_boundary_enumerates_only_attached_sources(gamma):
    module, _ = gamma
    user32 = Mock()
    gdi32 = Mock()

    def enumerate_display(_device, index, display_pointer, _flags):
        if index >= 2:
            return False
        display = display_pointer._obj
        display.DeviceName = rf"\\.\DISPLAY{index + 1}"
        display.StateFlags = (
            module.DISPLAY_DEVICE_ATTACHED_TO_DESKTOP if index == 0 else 0
        )
        return True

    user32.EnumDisplayDevicesW.side_effect = enumerate_display
    api = module._Win32GammaAPI(user32=user32, gdi32=gdi32)

    assert api.enumerate_display_sources() == [r"\\.\DISPLAY1"]


def test_win32_boundary_deletes_dc_when_gamma_call_fails(gamma):
    module, _ = gamma
    user32 = Mock()
    gdi32 = Mock()
    gdi32.CreateDCW.return_value = 123
    gdi32.GetDeviceGammaRamp.return_value = False
    api = module._Win32GammaAPI(user32=user32, gdi32=gdi32)

    with pytest.raises(module.WindowsGammaError, match="Could not read"):
        api.get_gamma_ramp(r"\\.\DISPLAY1")
    gdi32.DeleteDC.assert_called_once_with(123)
