from quart import request, jsonify
import pyautogui
import struct
import asyncio
from modules.config import Config


async def touchpad():
    data = await request.get_data()
    x_percentage, y_percentage = struct.unpack('<ff', data)

    loop = asyncio.get_event_loop()
    # 将计算和执行动作放在单独的线程中
    result = await loop.run_in_executor(None, handle_touchpad, x_percentage, y_percentage)
    print(f"Received coordinates: x={result['x']}%, y={result['y']}%")
    return jsonify({"status": "success", "x": result['x'], "y": result['y']})


def handle_touchpad(x_percentage, y_percentage):
    screen_width, screen_height = pyautogui.size()
    if x_percentage != 0 or y_percentage != 0:
        x_move = (x_percentage / 100.0) * screen_width * Config.TPad_SENSITIVITY * 0.06
        y_move = (y_percentage / 100.0) * screen_height * Config.TPad_SENSITIVITY * 0.06
        pyautogui.moveRel(x_move, y_move, duration=0.05)
    return {'x': x_percentage, 'y': y_percentage}
