# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

import asyncio
import importlib
import importlib.util
import os
import sys
import types
from unittest.mock import Mock, call

import pytest


BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..")


@pytest.fixture(autouse=True)
def backend_on_path(monkeypatch):
    monkeypatch.syspath_prepend(BACKEND_DIR)


@pytest.fixture
def brightness_module(monkeypatch):
    fake_sbc = types.ModuleType("screen_brightness_control")
    fake_sbc.get_brightness = Mock()
    fake_sbc.set_brightness = Mock()
    fake_monitorcontrol = types.ModuleType("monitorcontrol")
    fake_monitorcontrol.get_monitors = Mock(return_value=[])
    monkeypatch.setitem(sys.modules, "screen_brightness_control", fake_sbc)
    monkeypatch.setitem(sys.modules, "monitorcontrol", fake_monitorcontrol)
    sys.modules.pop("HostCore.brightness_controller.windows", None)
    try:
        module = importlib.import_module("HostCore.brightness_controller.windows")
        module.WindowsGammaBrightness = Mock()
        module.WindowsBrightnessController._software_fallback_active = False
        module.WindowsBrightnessController._software_fallback_logged = False
        yield module, fake_sbc, fake_monitorcontrol
    finally:
        sys.modules.pop("HostCore.brightness_controller.windows", None)


def test_windows_brightness_get_returns_first_controllable_display(brightness_module):
    module, fake_sbc, _ = brightness_module
    fake_sbc.get_brightness.return_value = [None, 42.8, 70]

    assert module.WindowsBrightnessController().get_current_brightness() == 42


def test_windows_brightness_get_falls_back_to_software(brightness_module):
    module, fake_sbc, _ = brightness_module
    fake_sbc.get_brightness.return_value = [None, None]
    module.WindowsGammaBrightness.get_brightness.return_value = 73

    assert module.WindowsBrightnessController().get_current_brightness() == 73
    module.WindowsGammaBrightness.get_brightness.assert_called_once_with()


def test_windows_brightness_set_updates_all_displays(brightness_module):
    module, fake_sbc, _ = brightness_module

    module.WindowsBrightnessController().set_brightness(55)

    fake_sbc.set_brightness.assert_called_once_with(55, no_return=False)
    module.WindowsGammaBrightness.set_brightness.assert_not_called()


class FakeMonitor:
    def __init__(self, luminance=None, error=None):
        self.luminance = luminance
        self.error = error
        self.get_luminance = Mock(side_effect=self._get_luminance)
        self.set_luminance = Mock(side_effect=self._set_luminance)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def _get_luminance(self):
        if self.error:
            raise self.error
        return self.luminance

    def _set_luminance(self, value):
        if self.error:
            raise self.error
        self.luminance = value


def test_windows_brightness_get_falls_back_to_monitorcontrol(brightness_module):
    module, fake_sbc, fake_monitorcontrol = brightness_module
    first = FakeMonitor(error=RuntimeError("first unavailable"))
    second = FakeMonitor(luminance=63)
    fake_sbc.get_brightness.side_effect = IndexError("display device index")
    fake_monitorcontrol.get_monitors.return_value = [first, second]

    assert module.WindowsBrightnessController().get_current_brightness() == 63
    first.get_luminance.assert_called_once_with()
    second.get_luminance.assert_called_once_with()


def test_windows_brightness_set_fallback_updates_each_available_monitor(brightness_module):
    module, fake_sbc, fake_monitorcontrol = brightness_module
    failed = FakeMonitor(error=RuntimeError("unsupported"))
    updated = FakeMonitor(luminance=10)
    fake_sbc.set_brightness.side_effect = IndexError("display device index")
    fake_monitorcontrol.get_monitors.return_value = [failed, updated]

    module.WindowsBrightnessController().set_brightness(55)

    failed.set_luminance.assert_called_once_with(55)
    updated.set_luminance.assert_called_once_with(55)
    assert updated.luminance == 55


def test_windows_brightness_set_falls_back_to_software(brightness_module):
    module, fake_sbc, fake_monitorcontrol = brightness_module
    fake_sbc.set_brightness.side_effect = IndexError("display device index")
    fake_monitorcontrol.get_monitors.return_value = [
        FakeMonitor(error=RuntimeError("unsupported"))
    ]

    module.WindowsBrightnessController().set_brightness(55)

    module.WindowsGammaBrightness.set_brightness.assert_called_once_with(55)
    assert module.WindowsBrightnessController._software_fallback_active is True


def test_windows_brightness_software_takeover_skips_hardware_on_later_sets(
    brightness_module,
):
    module, fake_sbc, fake_monitorcontrol = brightness_module
    fake_sbc.set_brightness.side_effect = IndexError("display device index")
    monitor = FakeMonitor(error=RuntimeError("unsupported"))
    fake_monitorcontrol.get_monitors.return_value = [monitor]
    controller = module.WindowsBrightnessController()

    controller.set_brightness(55)
    controller.set_brightness(45)

    fake_sbc.set_brightness.assert_called_once_with(55, no_return=False)
    fake_monitorcontrol.get_monitors.assert_called_once_with()
    monitor.set_luminance.assert_called_once_with(55)
    assert module.WindowsGammaBrightness.set_brightness.call_args_list == [
        call(55),
        call(45),
    ]


def test_windows_brightness_raises_unsupported_when_all_backends_fail(brightness_module):
    module, fake_sbc, fake_monitorcontrol = brightness_module
    fake_sbc.set_brightness.side_effect = RuntimeError("large SBC failure")
    fake_monitorcontrol.get_monitors.side_effect = RuntimeError("large DDC failure")
    module.WindowsGammaBrightness.set_brightness.side_effect = RuntimeError("GDI failure")

    with pytest.raises(
        module.BrightnessUnsupportedError,
        match="This device does not support brightness control",
    ):
        module.WindowsBrightnessController().set_brightness(55)
    assert module.WindowsBrightnessController._software_fallback_active is False


def test_windows_brightness_get_raises_unsupported_when_all_backends_fail(
    brightness_module,
):
    module, fake_sbc, fake_monitorcontrol = brightness_module
    fake_sbc.get_brightness.side_effect = RuntimeError("large SBC failure")
    fake_monitorcontrol.get_monitors.side_effect = RuntimeError("large DDC failure")
    module.WindowsGammaBrightness.get_brightness.side_effect = RuntimeError("GDI failure")

    with pytest.raises(module.BrightnessUnsupportedError):
        module.WindowsBrightnessController().get_current_brightness()


def test_windows_brightness_hardware_priority_skips_software(brightness_module):
    module, fake_sbc, fake_monitorcontrol = brightness_module
    fake_sbc.get_brightness.side_effect = RuntimeError("SBC unavailable")
    monitor = FakeMonitor(luminance=61)
    fake_monitorcontrol.get_monitors.return_value = [monitor]

    assert module.WindowsBrightnessController().get_current_brightness() == 61
    module.WindowsGammaBrightness.get_brightness.assert_not_called()


def test_windows_brightness_logs_software_fallback_only_once(
    brightness_module, monkeypatch
):
    module, fake_sbc, fake_monitorcontrol = brightness_module
    fake_sbc.get_brightness.side_effect = RuntimeError("unavailable")
    fake_monitorcontrol.get_monitors.return_value = []
    module.WindowsGammaBrightness.get_brightness.return_value = 100
    log_console = Mock()
    monkeypatch.setattr(module.LogManager, "log_console", log_console)

    controller = module.WindowsBrightnessController()
    controller.get_current_brightness()
    controller.get_current_brightness()

    fake_sbc.get_brightness.assert_called_once_with()
    fake_monitorcontrol.get_monitors.assert_called_once_with()
    assert module.WindowsGammaBrightness.get_brightness.call_count == 2
    log_console.assert_called_once_with(
        "Hardware brightness unavailable; using software dimming."
    )


@pytest.mark.parametrize("os_name", ["Linux", "UnknownOS"])
def test_unsupported_brightness_factory_logs_and_returns_none(monkeypatch, os_name):
    from HostCore import brightness_controller

    log_console = Mock()
    monkeypatch.setattr(brightness_controller, "get_platform", lambda: os_name)
    monkeypatch.setattr(brightness_controller.LogManager, "log_console", log_console)

    assert brightness_controller.get_brightness_controller() is None
    assert os_name in log_console.call_args.args[0]


def request_to_route(module, handler, method, data=None):
    quart = pytest.importorskip("quart")
    app = quart.Quart(__name__)
    app.route("/test", methods=[method])(handler)

    async def send():
        response = await app.test_client().open("/test", method=method, data=data)
        return response.status_code, await response.get_json()

    return asyncio.run(send())


@pytest.fixture
def brightness_route():
    pytest.importorskip("quart")
    route_path = os.path.join(
        BACKEND_DIR, "HostCore", "http_server", "route", "brightness.py"
    )
    spec = importlib.util.spec_from_file_location(
        "brightness_route_under_test", route_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_brightness_routes_success_and_invalid_range(brightness_route, monkeypatch):
    controller = Mock()
    controller.get_current_brightness.return_value = 65
    monkeypatch.setattr(brightness_route, "get_brightness_controller", lambda: controller)
    monkeypatch.setattr(brightness_route.LogManager, "log_console", Mock())

    status, payload = request_to_route(brightness_route, brightness_route.brightness_get, "GET")
    assert status == 200
    assert payload == {"status": "success", "brightness": 65}

    status, payload = request_to_route(brightness_route, brightness_route.brightness_set, "POST", "42")
    assert status == 200
    assert payload["status"] == "success"
    controller.set_brightness.assert_called_once_with(42)

    status, payload = request_to_route(brightness_route, brightness_route.brightness_set, "POST", "101")
    assert status == 200
    assert payload == {"status": "error", "message": "Invalid brightness value."}
    controller.set_brightness.assert_called_once()


def test_unsupported_brightness_routes_are_no_ops(brightness_route, monkeypatch):
    monkeypatch.setattr(brightness_route, "get_brightness_controller", lambda: None)
    monkeypatch.setattr(brightness_route.LogManager, "log_console", Mock())

    status, payload = request_to_route(brightness_route, brightness_route.brightness_get, "GET")
    assert status == 200
    assert payload == {
        "status": "success",
        "brightness": 0,
        "message": "Brightness control ignored.",
    }

    status, payload = request_to_route(brightness_route, brightness_route.brightness_set, "POST", "42")
    assert status == 200
    assert payload == {"status": "success", "message": "Brightness control ignored."}


@pytest.mark.parametrize(
    ("handler_name", "method", "data"),
    (("brightness_get", "GET", None), ("brightness_set", "POST", "42")),
)
def test_brightness_routes_report_unsupported_cleanly(
    brightness_route, monkeypatch, handler_name, method, data
):
    from HostCore.brightness_controller.base import BrightnessUnsupportedError

    controller = Mock()
    controller.get_current_brightness.side_effect = BrightnessUnsupportedError()
    controller.set_brightness.side_effect = BrightnessUnsupportedError()
    log_console = Mock()
    monkeypatch.setattr(brightness_route, "get_brightness_controller", lambda: controller)
    monkeypatch.setattr(brightness_route.LogManager, "log_console", log_console)

    status, payload = request_to_route(
        brightness_route, getattr(brightness_route, handler_name), method, data
    )

    assert status == 200
    assert payload == {
        "status": "error",
        "message": "Brightness control is not supported on this device.",
    }
    log_console.assert_called_once_with(
        "Brightness control is not supported on this device."
    )
