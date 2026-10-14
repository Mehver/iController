# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

import os
import threading
from unittest.mock import Mock

import pytest


BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..")


@pytest.fixture(autouse=True)
def backend_on_path(monkeypatch):
    monkeypatch.syspath_prepend(BACKEND_DIR)


def test_warmup_failure_does_not_stop_other_control(monkeypatch):
    from HostCore import control_warmup

    volume_started = threading.Event()
    brightness_controller = Mock()
    brightness_controller.get_current_brightness.side_effect = RuntimeError(
        "brightness unavailable"
    )
    volume_controller = Mock()

    def get_brightness_controller():
        assert volume_started.wait(timeout=1)
        return brightness_controller

    def get_volume_controller():
        volume_started.set()
        return volume_controller

    log_console = Mock()
    monkeypatch.setattr(
        control_warmup, "get_brightness_controller", get_brightness_controller
    )
    monkeypatch.setattr(control_warmup, "get_volume_controller", get_volume_controller)
    monkeypatch.setattr(control_warmup.LogManager, "log_console", log_console)

    control_warmup.warmup_controls()

    volume_controller.get_current_volume.assert_called_once_with()
    log_console.assert_called_once_with(
        "Brightness control warmup skipped: brightness unavailable"
    )


def test_warmup_brightness_unsupported_does_not_raise(monkeypatch):
    from HostCore import control_warmup

    brightness_controller = Mock()
    brightness_controller.get_current_brightness.side_effect = (
        control_warmup.BrightnessUnsupportedError()
    )
    log_console = Mock()
    monkeypatch.setattr(
        control_warmup, "get_brightness_controller", lambda: brightness_controller
    )
    monkeypatch.setattr(control_warmup, "get_volume_controller", lambda: None)
    monkeypatch.setattr(control_warmup.LogManager, "log_console", log_console)

    control_warmup.warmup_controls()

    log_console.assert_called_once_with(
        "Brightness control warmup skipped: device unsupported."
    )
