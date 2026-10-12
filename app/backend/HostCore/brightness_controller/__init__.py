# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

from HostCore.brightness_controller.base import BaseBrightnessController
from HostCore.infra.files.log_manager import LogManager
from HostCore.utils.check_platform import get_platform


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
