# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

import asyncio
import importlib.util
import os
import threading
from unittest.mock import Mock

import pytest


quart = pytest.importorskip("quart")
BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..")


def load_route(name):
    route_path = os.path.join(
        BACKEND_DIR, "HostCore", "http_server", "route", f"{name}.py"
    )
    spec = importlib.util.spec_from_file_location(
        f"{name}_threading_route_under_test", route_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("route_name", "handler_name", "factory_name", "getter_name", "value"),
    (
        (
            "brightness",
            "brightness_get",
            "get_brightness_controller",
            "get_current_brightness",
            61,
        ),
        ("volume", "volume_get", "get_volume_controller", "get_current_volume", 42),
    ),
)
def test_control_factory_runs_outside_event_loop(
    monkeypatch, route_name, handler_name, factory_name, getter_name, value
):
    monkeypatch.syspath_prepend(BACKEND_DIR)
    route = load_route(route_name)
    controller = Mock()
    factory_started = threading.Event()
    heartbeat = threading.Event()
    factory_observations = []
    worker_thread_ids = []

    def get_value():
        worker_thread_ids.append(threading.get_ident())
        return value

    getattr(controller, getter_name).side_effect = get_value

    def blocking_factory():
        worker_thread_ids.append(threading.get_ident())
        factory_started.set()
        factory_observations.append(heartbeat.wait(timeout=0.5))
        return controller

    monkeypatch.setattr(route, factory_name, blocking_factory)
    monkeypatch.setattr(route.LogManager, "log_console", Mock())

    async def exercise_route():
        event_loop_thread = threading.get_ident()

        async def pulse_heartbeat():
            while not factory_started.is_set():
                await asyncio.sleep(0)
            heartbeat.set()

        app = quart.Quart(__name__)
        app.route("/test", methods=["GET"])(getattr(route, handler_name))
        heartbeat_task = asyncio.create_task(pulse_heartbeat())
        response = await app.test_client().get("/test")
        await heartbeat_task
        return event_loop_thread, await response.get_json()

    event_loop_thread, payload = asyncio.run(exercise_route())

    assert factory_observations == [True]
    assert payload[route_name] == value
    # The controller factory and getter are both reached by the same sync helper.
    assert getattr(controller, getter_name).call_count == 1
    assert len(set(worker_thread_ids)) == 1
    assert worker_thread_ids[0] != event_loop_thread
