# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

"""Stdlib tests of the production COM boundary using fake native modules."""

from pathlib import Path
import sys
import threading
import types
import unittest
from unittest.mock import Mock, patch


CONTROLLER_PATH = Path(__file__).resolve().parents[1] / "HostCore/volume_controller/windows.py"
CHANGED_MODE = (-2147417850, 0x80010106)


class FakeCOMError(Exception):
    def __init__(self, code):
        super().__init__(code, "COM failure", None)
        self.hresult = code


def init_error(shape, code):
    if shape == "hresult":
        return FakeCOMError(code)
    error = OSError(code, "Windows COM failure")
    if shape == "winerror":
        error.winerror = code
        error.args = ("message, not a numeric HRESULT",)
    return error


class WindowsVolumeTests(unittest.TestCase):
    def setUp(self):
        self.load_controller()

    def load_controller(self):
        self.endpoint = Mock()
        self.endpoint.GetMasterVolumeLevelScalar.return_value = 0.42
        speakers = types.SimpleNamespace(EndpointVolume=self.endpoint)
        self.audio = Mock()
        self.audio.GetSpeakers.return_value = speakers
        self.com = types.ModuleType("comtypes")
        self.com.COMError = FakeCOMError
        self.com.COINIT_MULTITHREADED = 0
        self.com.CoInitializeEx = Mock(return_value=None)
        self.com.CoUninitialize = Mock()
        dependencies = {
            "HostCore.volume_controller.base": types.SimpleNamespace(BaseVolumeController=object),
            "pycaw": types.ModuleType("pycaw"),
            "pycaw.pycaw": types.SimpleNamespace(AudioUtilities=self.audio),
            "comtypes": self.com,
        }
        namespace = {"__name__": "volume_controller_under_test"}
        with patch.dict(sys.modules, dependencies):
            # Compile current source directly: never load a cached controller pyc.
            exec(compile(CONTROLLER_PATH.read_text(encoding="utf-8"), str(CONTROLLER_PATH), "exec"), namespace)
        self.controller = namespace["WindowsVolumeController"]

    def assert_init_failure_did_not_access_endpoint(self):
        self.audio.GetSpeakers.assert_not_called()
        self.endpoint.Release.assert_not_called()
        self.com.CoUninitialize.assert_not_called()

    # Keep the three original regression cases executable without pytest.
    def test_get_volume_uses_and_cleans_up_same_call(self):
        self.assertEqual(self.controller().get_current_volume(), 42)
        self.com.CoInitializeEx.assert_called_once_with(self.com.COINIT_MULTITHREADED)
        self.audio.GetSpeakers.assert_called_once_with()
        self.endpoint.GetMasterVolumeLevelScalar.assert_called_once_with()
        self.endpoint.Release.assert_called_once_with()
        self.com.CoUninitialize.assert_called_once_with()

    def test_set_volume_uses_endpoint_and_cleans_up(self):
        self.controller().set_volume(60)
        self.com.CoInitializeEx.assert_called_once_with(self.com.COINIT_MULTITHREADED)
        self.audio.GetSpeakers.assert_called_once_with()
        self.endpoint.SetMute.assert_called_once_with(0, None)
        self.endpoint.SetMasterVolumeLevelScalar.assert_called_once_with(0.6, None)
        self.endpoint.Release.assert_called_once_with()
        self.com.CoUninitialize.assert_called_once_with()

    def test_set_volume_propagates_errors_and_cleans_up(self):
        error = RuntimeError("set failed")
        self.endpoint.SetMute.side_effect = error
        with self.assertRaises(RuntimeError) as raised:
            self.controller().set_volume(60)
        self.assertIs(raised.exception, error)
        self.endpoint.SetMute.assert_called_once_with(0, None)
        self.endpoint.SetMasterVolumeLevelScalar.assert_not_called()
        self.endpoint.Release.assert_called_once_with()
        self.com.CoUninitialize.assert_called_once_with()

    def test_changed_mode_variants_borrow_existing_apartment_for_get_and_set(self):
        for shape in ("hresult", "winerror", "args"):
            for code in CHANGED_MODE:
                for operation in ("get", "set"):
                    with self.subTest(shape=shape, code=code, operation=operation):
                        self.load_controller()
                        self.com.CoInitializeEx.side_effect = init_error(shape, code)
                        if operation == "get":
                            self.assertEqual(self.controller().get_current_volume(), 42)
                            self.endpoint.GetMasterVolumeLevelScalar.assert_called_once_with()
                        else:
                            self.controller().set_volume(60)
                            self.endpoint.SetMute.assert_called_once_with(0, None)
                            self.endpoint.SetMasterVolumeLevelScalar.assert_called_once_with(0.6, None)
                        self.audio.GetSpeakers.assert_called_once_with()
                        self.endpoint.Release.assert_called_once_with()
                        self.com.CoUninitialize.assert_not_called()

    def test_s_ok_s_false_and_wrapper_none_each_balance_one_initialization(self):
        for result in (0, 1, None):
            with self.subTest(result=result):
                self.load_controller()
                self.com.CoInitializeEx.return_value = result
                self.assertEqual(self.controller().get_current_volume(), 42)
                self.com.CoUninitialize.assert_called_once_with()

    def test_other_initialization_errors_propagate_without_endpoint_or_uninit(self):
        for shape in ("hresult", "winerror", "args"):
            for code in (-2147467259, 0x80004005):
                with self.subTest(shape=shape, code=code):
                    self.load_controller()
                    error = init_error(shape, code)
                    self.com.CoInitializeEx.side_effect = error
                    with self.assertRaises(type(error)) as raised:
                        self.controller().get_current_volume()
                    self.assertIs(raised.exception, error)
                    self.assert_init_failure_did_not_access_endpoint()

    def test_message_text_and_unrelated_exception_with_rpc_number_are_not_swallowed(self):
        for error in (OSError("RPC_E_CHANGED_MODE 0x80010106"),
                      RuntimeError(CHANGED_MODE[0]), OSError("not numeric")):
            with self.subTest(error=error):
                self.load_controller()
                self.com.CoInitializeEx.side_effect = error
                with self.assertRaises(type(error)) as raised:
                    self.controller().get_current_volume()
                self.assertIs(raised.exception, error)
                self.assert_init_failure_did_not_access_endpoint()

    def test_authoritative_hresult_or_winerror_does_not_fall_back_to_conflicting_args(self):
        for error in (FakeCOMError(0x80004005), OSError(0x80004005, "init failed")):
            with self.subTest(error=error):
                self.load_controller()
                if isinstance(error, OSError):
                    error.winerror = 0x80004005
                error.args = (CHANGED_MODE[0], "conflicting args")
                self.com.CoInitializeEx.side_effect = error
                with self.assertRaises(type(error)):
                    self.controller().get_current_volume()
                self.assert_init_failure_did_not_access_endpoint()

    def test_operation_failure_on_existing_apartment_releases_but_never_uninitializes(self):
        for operation in ("get", "set"):
            for kind in ("runtime", "hresult", "winerror"):
                with self.subTest(operation=operation, error=kind):
                    self.load_controller()
                    self.com.CoInitializeEx.side_effect = init_error("winerror", CHANGED_MODE[0])
                    error = RuntimeError("endpoint failed") if kind == "runtime" else init_error(kind, CHANGED_MODE[0])
                    if operation == "get":
                        self.endpoint.GetMasterVolumeLevelScalar.side_effect = error
                        call = self.controller().get_current_volume
                    else:
                        self.endpoint.SetMute.side_effect = error
                        call = lambda: self.controller().set_volume(60)
                    with self.assertRaises(type(error)) as raised:
                        call()
                    self.assertIs(raised.exception, error)  # RPC errors outside init are not swallowed.
                    self.endpoint.Release.assert_called_once_with()
                    self.com.CoUninitialize.assert_not_called()

    def test_init_endpoint_operation_and_release_remain_on_the_calling_thread(self):
        calls = []
        self.com.CoInitializeEx.side_effect = lambda flags: calls.append(("init", threading.get_ident()))
        self.audio.GetSpeakers.side_effect = lambda: calls.append(("endpoint", threading.get_ident())) or types.SimpleNamespace(EndpointVolume=self.endpoint)
        self.endpoint.GetMasterVolumeLevelScalar.side_effect = lambda: calls.append(("get", threading.get_ident())) or .42
        self.endpoint.Release.side_effect = lambda: calls.append(("release", threading.get_ident()))
        self.com.CoUninitialize.side_effect = lambda: calls.append(("uninit", threading.get_ident()))
        self.assertEqual(self.controller().get_current_volume(), 42)
        self.assertEqual([name for name, _ in calls], ["init", "endpoint", "get", "release", "uninit"])
        self.assertEqual({identity for _, identity in calls}, {threading.get_ident()})


if __name__ == "__main__":
    unittest.main()
