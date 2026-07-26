# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

class BaseVolumeController:
    def get_current_volume(self):
        raise NotImplementedError("This method is not implemented.")

    def set_volume(self, target_volume):
        raise NotImplementedError("This method is not implemented.")
