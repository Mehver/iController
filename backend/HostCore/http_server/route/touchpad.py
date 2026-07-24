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

import threading
import pyautogui
import struct
from quart import request, jsonify
from HostCore.infra.files.config import Config
from HostCore.infra.files.log_manager import LogManager


def handle_touchpad(data):
    """Use by touchpad(), call by threading to reduce delay."""
    x_percentage, y_percentage = struct.unpack('<ff', data)
    screen_width, screen_height = pyautogui.size()
    if x_percentage != 0 or y_percentage != 0:
        x_move = (x_percentage / 100.0) * screen_width * Config.Control.TPad_SENSITIVITY * 0.06
        y_move = (y_percentage / 100.0) * screen_height * Config.Control.TPad_SENSITIVITY * 0.06
        pyautogui.FAILSAFE = False
        pyautogui.moveRel(x_move, y_move, duration=0.05)
        LogManager.log_console(f"Touchpad received coordinates: x={x_percentage:07.2f}%, y={y_percentage:07.2f}%.")


async def touchpad():
    """app.route('/api/touchpad', methods=['POST'])(touchpad)"""
    data = await request.get_data()
    # Use threading to reduce delay
    thread = threading.Thread(target=handle_touchpad, args=(data,))
    thread.start()
    return jsonify({"status": "success", "message": "Touchpad request is being processed."})


async def touchpad_reposition():
    """app.route('/api/touchpad/reposition', methods=['POST'])(touchpad_reposition)"""
    # 鼠标回到屏幕中间
    pyautogui.moveTo(pyautogui.size()[0] / 2, pyautogui.size()[1] / 2, duration=0.25)
    LogManager.log_console("Touchpad has been repositioned to the center of the screen.")
    return jsonify({"status": "success", "message": "Touchpad has been repositioned."})
