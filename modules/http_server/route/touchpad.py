import threading
import pyautogui
import struct
from quart import request, jsonify
from modules.config import Config


def handle_touchpad(data):
    """
    Use by touchpad(), call by threading to reduce delay.
    """
    x_percentage, y_percentage = struct.unpack('<ff', data)
    screen_width, screen_height = pyautogui.size()
    if x_percentage != 0 or y_percentage != 0:
        x_move = (x_percentage / 100.0) * screen_width * Config.Control.TPad_SENSITIVITY * 0.06
        y_move = (y_percentage / 100.0) * screen_height * Config.Control.TPad_SENSITIVITY * 0.06
        pyautogui.FAILSAFE = False
        pyautogui.moveRel(x_move, y_move, duration=0.05)
        print(f"Touchpad received coordinates: x={x_percentage:07.2f}%, y={y_percentage:07.2f}%.")


async def touchpad():
    """
    app.route('/api/touchpad', methods=['POST'])(touchpad)
    """
    data = await request.get_data()
    # Use threading to reduce delay
    thread = threading.Thread(target=handle_touchpad, args=(data,))
    thread.start()
    return jsonify({"status": "success", "message": "Touchpad request is being processed."})


async def touchpad_reposition():
    """
    app.route('/api/touchpad/reposition', methods=['POST'])(touchpad_reposition)
    """
    # 鼠标回到屏幕中间
    pyautogui.moveTo(pyautogui.size()[0] / 2, pyautogui.size()[1] / 2, duration=0.25)
    print("Touchpad has been repositioned to the center of the screen.")
    return jsonify({"status": "success", "message": "Touchpad has been repositioned."})
