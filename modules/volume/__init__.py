from modules.volume.base import BaseVolumeController
from modules.volume.windows import WindowsVolumeController
from modules.volume.mac import MacVolumeController
import platform


def get_volume_controller() -> BaseVolumeController:
    os_name = platform.system()
    if os_name == 'Windows':
        return WindowsVolumeController()
    elif os_name == 'Darwin':  # macOS的官方名称是Darwin
        return MacVolumeController()
    else:
        raise NotImplementedError("This OS is not supported for volume control.")

