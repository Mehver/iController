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

from quart import jsonify, request
import pyautogui
import pyperclip
import platform
from HostCore.infra.files.log_manager import LogManager
from HostCore.infra.files.config import Config


def keyboard_log_text_payload(text):
    if Config.Log.KEYBOARD_TEXT_LOG:
        return f"\"{text}\""
    return f"[length={len(text)}]"


async def keyboard_buttons():
    """app.route('/api/keyboard/buttons', methods=['POST'])(keyboard_buttons)"""
    signal = (await request.get_data()).decode('utf-8')
    if signal == 'Backspace':
        pyautogui.press('backspace')
        action = "press backspace"
    elif signal == 'Enter':
        pyautogui.press('enter')
        action = "press enter"
    else:
        return "Invalid signal", 400
    LogManager.log_console(f"Keyboard performed {action}.")
    return jsonify({"status": "success", "action": action})


async def keyboard_typewriting():
    """app.route('/api/keyboard/typewriting', methods=['POST'])(keyboard_typewriting)"""
    text = (await request.get_data()).decode('utf-8')
    text_payload = keyboard_log_text_payload(text)
    try:
        pyautogui.write(text, interval=0.05)
        LogManager.log_console(f"Keyboard typewriting: {text_payload}.")
        return jsonify({"status": "success", "message": "Text has been sent successfully."})
    except Exception as e:
        LogManager.log_console(f"Keyboard typewriting error after input {text_payload}: {e}.")
        return jsonify({"status": "error", "message": "An error occurred while sending text."}), 500


async def keyboard_pastetext():
    """app.route('/api/keyboard/pastetext', methods=['POST'])(keyboard_pastetext)"""
    text = (await request.get_data()).decode('utf-8')
    text_payload = keyboard_log_text_payload(text)
    os_name = platform.system()
    if os_name == 'Windows':
        try:
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            LogManager.log_console(f"Keyboard paste text: {text_payload}.")
            return jsonify({"status": "success", "message": "Text has been pasted successfully."})
        except Exception as e:
            LogManager.log_console(f"Keyboard paste text error after input {text_payload}: {e}.")
            return jsonify({"status": "error", "message": "An error occurred while pasting text."}), 500
    elif os_name == 'Darwin':
        try:
            pyautogui.write(text, interval=0.05)
            return jsonify({"status": "success", "message": "Text has been sent successfully."})
        except Exception as e:
            LogManager.log_console(f"Keyboard paste text error after input {text_payload}: {e}.")
            return jsonify({"status": "error", "message": "An error occurred while sending text."}), 500
