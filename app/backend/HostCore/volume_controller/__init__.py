# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

from HostCore.volume_controller.base import BaseVolumeController
from HostCore.infra.files.log_manager import LogManager
from HostCore.utils.check_platform import get_platform


def get_volume_controller() -> BaseVolumeController | None:
    os_name = get_platform()
    if os_name == 'Windows':
        from HostCore.volume_controller.windows import WindowsVolumeController
        return WindowsVolumeController()
    elif os_name == 'Darwin':
        from HostCore.volume_controller.mac import MacVolumeController
        return MacVolumeController()
    else:
        # TODO: Add volume control support for other operating systems.
        LogManager.log_console(
            f"Volume control ignored: {os_name} is not currently supported."
        )
        return None
