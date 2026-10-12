# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause


class BaseBrightnessController:
    def get_current_brightness(self):
        raise NotImplementedError("This method is not implemented.")

    def set_brightness(self, target_brightness):
        raise NotImplementedError("This method is not implemented.")
