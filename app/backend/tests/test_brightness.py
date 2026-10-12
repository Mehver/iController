# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

import asyncio
import importlib
import importlib.util
import os
import sys
import types
from unittest.mock import Mock

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
    monkeypatch.setitem(sys.modules, "screen_brightness_control", fake_sbc)
    sys.modules.pop("HostCore.brightness_controller.windows", None)
    try:
        module = importlib.import_module("HostCore.brightness_controller.windows")
        yield module, fake_sbc
    finally:
        sys.modules.pop("HostCore.brightness_controller.windows", None)


def test_windows_brightness_get_returns_first_controllable_display(brightness_module):
    module, fake_sbc = brightness_module
    fake_sbc.get_brightness.return_value = [None, 42.8, 70]

    assert module.WindowsBrightnessController().get_current_brightness() == 42


def test_windows_brightness_get_raises_without_controllable_display(brightness_module):
    module, fake_sbc = brightness_module
    fake_sbc.get_brightness.return_value = [None, None]

    with pytest.raises(RuntimeError, match="No controllable display found"):
        module.WindowsBrightnessController().get_current_brightness()


def test_windows_brightness_set_updates_all_displays(brightness_module):
    module, fake_sbc = brightness_module

    module.WindowsBrightnessController().set_brightness(55)

    fake_sbc.set_brightness.assert_called_once_with(55, no_return=False)


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
