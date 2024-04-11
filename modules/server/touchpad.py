from flask import request, jsonify
import pyautogui
import struct
from modules.config import Config


def touchpad():
    data = request.data
    x_percentage, y_percentage = struct.unpack('<ff', data)
    screen_width, screen_height = pyautogui.size()
    if x_percentage == 0 and y_percentage == 0:
        pass
    else:
        x_move = (x_percentage / 100.0) * screen_width * Config.TPad_SENSITIVITY * 0.06
        y_move = (y_percentage / 100.0) * screen_height * Config.TPad_SENSITIVITY * 0.06
        pyautogui.moveRel(x_move, y_move, duration=0.05)
    print(f"Received coordinates: x={x_percentage}%, y={y_percentage}%")
    return jsonify({"status": "success", "x": x_percentage, "y": y_percentage})
