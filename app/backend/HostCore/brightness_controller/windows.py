# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

import screen_brightness_control as sbc

from HostCore.brightness_controller.base import BaseBrightnessController


class WindowsBrightnessController(BaseBrightnessController):
    def get_current_brightness(self):
        brightness_values = sbc.get_brightness()
        for brightness in brightness_values:
            if brightness is not None:
                return int(brightness)
        raise RuntimeError("No controllable display found.")

    def set_brightness(self, target_brightness):
        sbc.set_brightness(target_brightness, no_return=False)
