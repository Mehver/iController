from modules.volume.base import BaseVolumeController
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL, CoInitializeEx, COINIT_MULTITHREADED
from ctypes import cast, POINTER


class WindowsVolumeController(BaseVolumeController):
    def __init__(self):
        # 正确初始化COM库
        CoInitializeEx(COINIT_MULTITHREADED)

        devices = AudioUtilities.GetSpeakers()
        # noinspection PyProtectedMember
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

    def get_current_volume(self):
        return self.volume.GetMasterVolumeLevelScalar() * 100

    def set_volume(self, target_volume):
        # 确保没用静音
        self.volume.SetMute(0, None)
        # 设置音量
        self.volume.SetMasterVolumeLevelScalar(target_volume / 100, None)
