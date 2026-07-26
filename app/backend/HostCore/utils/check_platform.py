# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

import platform

def get_platform():
    return platform.system()

def is_mac():
    return get_platform() == "Darwin"
