from quart import request, jsonify
import pyautogui
from modules.config import Config
from modules.log_manager import LogManager


async def mousewheel():
    """app.route('/api/mousewheel', methods=['POST'])(mousewheel)"""
    raw_data = (await request.get_data(as_text=True)).strip()
    try:
        wheel_amount = int(raw_data)
        wheel_amount = wheel_amount * wheel_amount * wheel_amount * wheel_amount * wheel_amount
        wheel_amount = wheel_amount * Config.Control.MWheel_SENSITIVITY + Config.Control.MWheel_CONSTANT
        pyautogui.scroll(wheel_amount)
        LogManager.log_console(f"Mouse wheel scrolled {wheel_amount} steps.")
        return jsonify({"status": "success", "steps": wheel_amount})
    except ValueError as e:
        LogManager.log_console(f"Error converting data to int: {e}")
        return jsonify({"status": "error", "message": "Invalid data format"}), 400
