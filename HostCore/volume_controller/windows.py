from HostCore.volume_controller.base import BaseVolumeController
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL, CoInitializeEx, COINIT_MULTITHREADED, CoUninitialize
from ctypes import cast, POINTER
import threading
import atexit


class WindowsVolumeController(BaseVolumeController):
    def __init__(self):
        self.volume = None
        # 创建独立的线程控制音量，避免Windows的[WinError -2147417850]报错
        self.init_thread = threading.Thread(target=self.init_volume_control)
        self.init_thread.start()
        self.init_thread.join()  # 等待线程完成初始化

    def init_volume_control(self):
        # 初始化COM库
        CoInitializeEx(COINIT_MULTITHREADED)
        devices = AudioUtilities.GetSpeakers()
        # noinspection PyProtectedMember
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        atexit.register(self.cleanup_com)

    def cleanup_com(self):
        """确保 COM 对象在程序退出前正确释放"""
        if self.volume:
            # 显式释放 COM 对象
            self.volume.Release()
        CoUninitialize()

    def get_current_volume(self):
        # 在同一个线程中调用
        return self.volume.GetMasterVolumeLevelScalar() * 100

    def set_volume(self, target_volume):
        # 在独立的线程中调用
        def set_vol():
            self.volume.SetMute(0, None)
            self.volume.SetMasterVolumeLevelScalar(target_volume / 100, None)
        thread = threading.Thread(target=set_vol)
        thread.start()
        thread.join()
