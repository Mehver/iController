from modules.volumeController.base import BaseVolumeController
import os


class MacVolumeController(BaseVolumeController):
    def get_current_volume(self):
        volume_info = os.popen("osascript -e 'output volume of (get volume settings)'").read().strip()
        return int(volume_info)

    def set_volume(self, target_volume):
        os.system(f"osascript -e 'set volume output volume {target_volume}'")
