from modules.volume.base import BaseVolumeController
import platform


def get_volume_controller() -> BaseVolumeController:
    os_name = platform.system()
    if os_name == 'Windows':
        from modules.volume.windows import WindowsVolumeController
        return WindowsVolumeController()
    elif os_name == 'Darwin':
        from modules.volume.mac import MacVolumeController
        return MacVolumeController()
    else:
        raise NotImplementedError("This OS is not supported for volume control")

