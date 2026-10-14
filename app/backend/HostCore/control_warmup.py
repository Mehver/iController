# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

from concurrent.futures import ThreadPoolExecutor

from HostCore.brightness_controller import get_brightness_controller
from HostCore.brightness_controller.base import BrightnessUnsupportedError
from HostCore.infra.files.log_manager import LogManager
from HostCore.volume_controller import get_volume_controller


def _log_warning(message):
    try:
        LogManager.log_console(message)
    except Exception:
        # Logging must not turn an optional warmup into a startup failure.
        pass


def _warmup_brightness():
    try:
        controller = get_brightness_controller()
        if controller is not None:
            controller.get_current_brightness()
    except BrightnessUnsupportedError:
        _log_warning(
            "Brightness control warmup skipped: device unsupported."
        )
    except Exception as error:
        _log_warning(f"Brightness control warmup skipped: {error}")


def _warmup_volume():
    try:
        controller = get_volume_controller()
        if controller is not None:
            controller.get_current_volume()
    except Exception as error:
        _log_warning(f"Volume control warmup skipped: {error}")


def warmup_controls():
    """Initialize brightness and volume backends concurrently without HTTP."""
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = (
                executor.submit(_warmup_brightness),
                executor.submit(_warmup_volume),
            )
            for future in futures:
                future.result()
    except Exception as error:
        _log_warning(f"Control warmup skipped: {error}")
