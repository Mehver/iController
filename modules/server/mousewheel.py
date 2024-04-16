from quart import request, jsonify
import pyautogui
from modules.config import Config


async def mousewheel():
    raw_data = (await request.get_data(as_text=True)).strip()
    try:
        wheel_amount = int(raw_data)
        wheel_amount = wheel_amount * wheel_amount * wheel_amount * wheel_amount * wheel_amount
        wheel_amount = wheel_amount * Config.MWheel_SENSITIVITY + Config.MWheel_CONSTANT
        pyautogui.scroll(wheel_amount)
        print(f"Scrolled {wheel_amount} steps")
        return jsonify({"status": "success", "steps": wheel_amount})
    except ValueError as e:
        print(f"Error converting data to int: {e}")
        return jsonify({"status": "error", "message": "Invalid data format"}), 400
