# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

import asyncio
import importlib.util
import os
import sys
import types
from unittest.mock import Mock

import pytest

quart = pytest.importorskip("quart")


BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..")


@pytest.fixture(autouse=True)
def backend_on_path(monkeypatch):
    monkeypatch.syspath_prepend(BACKEND_DIR)


def load_route(monkeypatch, name):
    """Load a route with inert input-library replacements for headless tests."""
    pyautogui = types.ModuleType("pyautogui")
    pyautogui.write = Mock()
    pyautogui.hotkey = Mock()
    pyperclip = types.ModuleType("pyperclip")
    pyperclip.copy = Mock()
    monkeypatch.setitem(sys.modules, "pyautogui", pyautogui)
    monkeypatch.setitem(sys.modules, "pyperclip", pyperclip)

    route_path = os.path.join(BACKEND_DIR, "HostCore", "http_server", "route", f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"{name}_route_under_test", route_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module.LogManager, "log_console", Mock())
    return module


def request_to_route(module, handler, method, data=None):
    app = quart.Quart(__name__)
    app.route("/test", methods=[method])(handler)

    async def send():
        response = await app.test_client().open("/test", method=method, data=data)
        return response.status_code, await response.get_json()

    return asyncio.run(send())


@pytest.mark.parametrize("os_name", ["Linux", "UnknownOS"])
def test_unsupported_utils_and_volume_factory_log_and_return_safe_values(monkeypatch, os_name):
    from HostCore.utils import check_ip, check_port
    from HostCore import volume_controller

    for module, expected in ((check_ip, None), (check_port, False)):
        log_console = Mock()
        monkeypatch.setattr(module, "get_platform", lambda: os_name)
        monkeypatch.setattr(module.LogManager, "log_console", log_console)
        result = module.check_ip() if module is check_ip else module.check_port(3030)
        assert result is expected
        assert os_name in log_console.call_args.args[0]

    log_console = Mock()
    monkeypatch.setattr(volume_controller, "get_platform", lambda: os_name)
    monkeypatch.setattr(volume_controller.LogManager, "log_console", log_console)
    assert volume_controller.get_volume_controller() is None
    assert os_name in log_console.call_args.args[0]


@pytest.mark.parametrize("os_name", ["Linux", "UnknownOS"])
def test_unsupported_keyboard_paste_is_a_no_op(monkeypatch, os_name):
    keyboard = load_route(monkeypatch, "keyboard")
    monkeypatch.setattr(keyboard.platform, "system", lambda: os_name)

    status, payload = request_to_route(keyboard, keyboard.keyboard_pastetext, "POST", "hello")

    assert status == 200
    assert payload["status"] == "success"
    assert os_name in keyboard.LogManager.log_console.call_args.args[0]
    keyboard.pyautogui.write.assert_not_called()
    keyboard.pyautogui.hotkey.assert_not_called()
    keyboard.pyperclip.copy.assert_not_called()


@pytest.mark.parametrize("os_name", ["Linux", "UnknownOS"])
def test_unsupported_volume_routes_are_no_ops_after_validation(monkeypatch, os_name):
    volume = load_route(monkeypatch, "volume")
    from HostCore import volume_controller

    log_console = Mock()
    monkeypatch.setattr(volume_controller, "get_platform", lambda: os_name)
    monkeypatch.setattr(volume_controller.LogManager, "log_console", log_console)
    monkeypatch.setattr(volume, "get_volume_controller", volume_controller.get_volume_controller)

    status, payload = request_to_route(volume, volume.volume_get, "GET")
    assert status == 200
    assert payload["status"] == "success"
    assert payload["volume"] == 0
    assert log_console.call_count == 1
    assert os_name in log_console.call_args.args[0]

    status, payload = request_to_route(volume, volume.volume_set, "POST", "42")
    assert status == 200
    assert payload["status"] == "success"
    assert log_console.call_count == 2

    status, payload = request_to_route(volume, volume.volume_set, "POST", "not-an-integer")
    assert status == 200
    assert payload["status"] == "error"
    assert log_console.call_count == 4
