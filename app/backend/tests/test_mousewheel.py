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


@pytest.fixture
def mousewheel_module(monkeypatch):
    """Load the route with a stubbed pyautogui module."""
    backend_dir = os.path.join(os.path.dirname(__file__), "..")
    monkeypatch.syspath_prepend(backend_dir)

    pyautogui = types.ModuleType("pyautogui")
    pyautogui.scroll = Mock()
    monkeypatch.setitem(sys.modules, "pyautogui", pyautogui)

    route_path = os.path.join(
        backend_dir, "HostCore", "http_server", "route", "mousewheel.py"
    )
    spec = importlib.util.spec_from_file_location(
        "mousewheel_route_under_test", route_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module.LogManager, "log_console", Mock())
    return module


def post_to_route(module, data):
    app = quart.Quart(__name__)
    app.route("/api/mousewheel", methods=["POST"])(module.mousewheel)

    async def post():
        response = await app.test_client().post("/api/mousewheel", data=data)
        return response.status_code, await response.get_json()

    return asyncio.run(post())


def test_fractional_sensitivity_sends_rounded_python_int(
    mousewheel_module, monkeypatch
):
    monkeypatch.setattr(
        mousewheel_module.Config.Control, "MWheel_SENSITIVITY", 0.5
    )
    monkeypatch.setattr(mousewheel_module.Config.Control, "MWheel_CONSTANT", 0)

    status_code, payload = post_to_route(mousewheel_module, "3")

    assert status_code == 200
    assert payload == {"status": "success", "steps": 122}
    mousewheel_module.pyautogui.scroll.assert_called_once_with(122)
    steps = mousewheel_module.pyautogui.scroll.call_args.args[0]
    assert type(steps) is int


def test_invalid_request_does_not_scroll(mousewheel_module):
    status_code, payload = post_to_route(mousewheel_module, "not-an-integer")

    assert status_code == 400
    assert payload == {"status": "error", "message": "Invalid data format"}
    mousewheel_module.pyautogui.scroll.assert_not_called()
