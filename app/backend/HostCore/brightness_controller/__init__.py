# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

from HostCore.brightness_controller.base import BaseBrightnessController
from HostCore.infra.files.log_manager import LogManager
from HostCore.utils.check_platform import get_platform
import threading


_bridge_lock = threading.Lock()
_overlay_bridge = None
_overlay_cleared = True
_brightness_closing = False


def register_overlay_bridge(bridge):
    """GUI registration only; neither Qt imports nor native-operation locks."""
    global _overlay_bridge, _overlay_cleared
    with _bridge_lock:
        if _overlay_bridge is not None or _brightness_closing:
            raise RuntimeError('Overlay bridge is already registered or shutting down.')
        _overlay_bridge, _overlay_cleared = bridge, False


def unregister_overlay_bridge(bridge, *, cleared, closing=False):
    global _overlay_bridge, _overlay_cleared, _brightness_closing
    with _bridge_lock:
        if closing:
            _brightness_closing = True
        if _overlay_bridge is bridge:
            _overlay_bridge, _overlay_cleared = None, cleared


def overlay_state():
    with _bridge_lock:
        return _overlay_bridge, _overlay_cleared, _brightness_closing


def get_brightness_controller() -> BaseBrightnessController | None:
    os_name = get_platform()
    if os_name == 'Windows':
        from HostCore.brightness_controller.windows import WindowsBrightnessController
        return WindowsBrightnessController()

    # TODO: Add brightness control support for other operating systems.
    LogManager.log_console(
        f"Brightness control ignored: {os_name} is not currently supported."
    )
    return None
