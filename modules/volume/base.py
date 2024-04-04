class BaseVolumeController:
    def get_current_volume(self):
        raise NotImplementedError("This method is not implemented.")

    def set_volume(self, target_volume):
        raise NotImplementedError("This method is not implemented.")
