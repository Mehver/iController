# BSD 3-Clause License
#
# Copyright (c) 2024 Mehver (https://github.com/Mehver). All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from HostCore.volume_controller.base import BaseVolumeController
from pycaw.pycaw import AudioUtilities
from comtypes import CoInitializeEx, COINIT_MULTITHREADED, CoUninitialize
import threading
import atexit


class WindowsVolumeController(BaseVolumeController):
    def __init__(self):
        self.volume = None
        self.init_thread = threading.Thread(target=self.init_volume_control)
        self.init_thread.start()
        self.init_thread.join()

    def init_volume_control(self):
        CoInitializeEx(COINIT_MULTITHREADED)
        devices = AudioUtilities.GetSpeakers()
        self.volume = devices.EndpointVolume
        atexit.register(self.cleanup_com)

    def cleanup_com(self):
        if self.volume:
            self.volume.Release()
        CoUninitialize()

    def get_current_volume(self):
        return self.volume.GetMasterVolumeLevelScalar() * 100

    def set_volume(self, target_volume):
        def set_vol():
            self.volume.SetMute(0, None)
            self.volume.SetMasterVolumeLevelScalar(target_volume / 100, None)
        thread = threading.Thread(target=set_vol)
        thread.start()
        thread.join()
