# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

import threading

import screen_brightness_control as sbc
from monitorcontrol import get_monitors

from HostCore.brightness_controller.base import (
    BaseBrightnessController,
    BrightnessUnsupportedError,
)
from HostCore.brightness_controller.windows_gamma import WindowsGammaBrightness
from HostCore.infra.files.log_manager import LogManager


class WindowsBrightnessController(BaseBrightnessController):
    _hardware_lock = threading.Lock()
    _software_fallback_active = False
    _software_fallback_logged = False

    @classmethod
    def _log_software_fallback_once(cls):
        if not cls._software_fallback_logged:
            LogManager.log_console(
                "Hardware brightness unavailable; using software dimming."
            )
            cls._software_fallback_logged = True

    def get_current_brightness(self):
        with self._hardware_lock:
            if self._software_fallback_active:
                try:
                    return WindowsGammaBrightness.get_brightness()
                except Exception:
                    raise BrightnessUnsupportedError() from None

            try:
                brightness_values = sbc.get_brightness()
                for brightness in brightness_values:
                    if brightness is not None:
                        return int(brightness)
            except Exception:
                pass

            try:
                monitors = get_monitors()
                for monitor in monitors:
                    try:
                        with monitor:
                            return int(monitor.get_luminance())
                    except Exception:
                        continue
            except Exception:
                pass

            try:
                brightness = WindowsGammaBrightness.get_brightness()
            except Exception:
                raise BrightnessUnsupportedError() from None
            self.__class__._software_fallback_active = True
            self._log_software_fallback_once()
            return brightness

    def set_brightness(self, target_brightness):
        with self._hardware_lock:
            if self._software_fallback_active:
                try:
                    WindowsGammaBrightness.set_brightness(target_brightness)
                    return
                except Exception:
                    raise BrightnessUnsupportedError() from None

            try:
                sbc.set_brightness(target_brightness, no_return=False)
                return
            except Exception:
                pass

            success = False
            try:
                monitors = get_monitors()
                for monitor in monitors:
                    try:
                        with monitor:
                            monitor.set_luminance(target_brightness)
                        success = True
                    except Exception:
                        continue
            except Exception:
                pass

            if success:
                return

            try:
                WindowsGammaBrightness.set_brightness(target_brightness)
            except Exception:
                raise BrightnessUnsupportedError() from None
            self.__class__._software_fallback_active = True
            self._log_software_fallback_once()
