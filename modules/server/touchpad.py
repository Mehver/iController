import threading
import pyautogui
import struct
from quart import request, jsonify
from modules.config import Config


def handle_touchpad(data):
    x_percentage, y_percentage = struct.unpack('<ff', data)
    screen_width, screen_height = pyautogui.size()
    if x_percentage != 0 or y_percentage != 0:
        x_move = (x_percentage / 100.0) * screen_width * Config.TPad_SENSITIVITY * 0.06
        y_move = (y_percentage / 100.0) * screen_height * Config.TPad_SENSITIVITY * 0.06
        pyautogui.FAILSAFE = False
        pyautogui.moveRel(x_move, y_move, duration=0.05)
        print(f"Touchpad received coordinates: x={x_percentage:07.2f}%, y={y_percentage:07.2f}%.")


async def touchpad():
    data = await request.get_data()
    thread = threading.Thread(target=handle_touchpad, args=(data,))
    thread.start()
    return jsonify({"status": "success", "message": "Touchpad request is being processed."})


async def touchpad_reposition():
    # 鼠标回到屏幕中间
    pyautogui.moveTo(pyautogui.size()[0] / 2, pyautogui.size()[1] / 2, duration=0.25)
    print("Touchpad has been repositioned to the center of the screen.")
    return jsonify({"status": "success", "message": "Touchpad has been repositioned."})
