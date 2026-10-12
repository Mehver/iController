# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

import threading

import screen_brightness_control as sbc
from monitorcontrol import get_monitors

from HostCore.brightness_controller.base import BaseBrightnessController


class WindowsBrightnessController(BaseBrightnessController):
    _hardware_lock = threading.Lock()

    def get_current_brightness(self):
        with self._hardware_lock:
            try:
                brightness_values = sbc.get_brightness()
                for brightness in brightness_values:
                    if brightness is not None:
                        return int(brightness)
                sbc_error = "no usable brightness value"
            except Exception as error:
                sbc_error = str(error)

            fallback_errors = []
            try:
                monitors = get_monitors()
                for monitor in monitors:
                    try:
                        with monitor:
                            return int(monitor.get_luminance())
                    except Exception as error:
                        fallback_errors.append(str(error))
                if not monitors:
                    fallback_errors.append("no monitors found")
            except Exception as error:
                fallback_errors.append(str(error))

            fallback_error = "; ".join(filter(None, fallback_errors)) or "no usable monitor"
            raise RuntimeError(
                f"Brightness control failed (SBC: {sbc_error}; fallback: {fallback_error})."
            )

    def set_brightness(self, target_brightness):
        with self._hardware_lock:
            try:
                sbc.set_brightness(target_brightness, no_return=False)
                return
            except Exception as error:
                sbc_error = str(error)

            fallback_errors = []
            success = False
            try:
                monitors = get_monitors()
                for monitor in monitors:
                    try:
                        with monitor:
                            monitor.set_luminance(target_brightness)
                        success = True
                    except Exception as error:
                        fallback_errors.append(str(error))
                if not monitors:
                    fallback_errors.append("no monitors found")
            except Exception as error:
                fallback_errors.append(str(error))

            if success:
                return

            fallback_error = "; ".join(filter(None, fallback_errors)) or "no usable monitor"
            raise RuntimeError(
                f"Brightness control failed (SBC: {sbc_error}; fallback: {fallback_error})."
            )
