from HostCore.volume_controller.base import BaseVolumeController
from HostCore.utils.check_platform import get_platform


def get_volume_controller() -> BaseVolumeController:
    os_name = get_platform()
    if os_name == 'Windows':
        from HostCore.volume_controller.windows import WindowsVolumeController
        return WindowsVolumeController()
    elif os_name == 'Darwin':
        from HostCore.volume_controller.mac import MacVolumeController
        return MacVolumeController()
    else:
        raise NotImplementedError(f"This OS ({os_name}) is not supported.")

