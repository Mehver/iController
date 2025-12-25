from quart import jsonify, request
import pyautogui
from HostCore.log_manager import LogManager


async def dpad():
    """app.route('/api/dpad', methods=['POST'])(dpad)"""
    signal = (await request.get_data()).decode('utf-8')
    if signal == 'DUp':
        pyautogui.press('up')
        action = "press up"
    elif signal == 'DLeft':
        pyautogui.press('left')
        action = "press left"
    elif signal == 'DDown':
        pyautogui.press('down')
        action = "press down"
    elif signal == 'DRight':
        pyautogui.press('right')
        action = "press right"
    else:
        return "Invalid signal", 400
    LogManager.log_console(f"D-Pad performed {action}.")
    return jsonify({"status": "success", "action": action})
