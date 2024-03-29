from flask import request, jsonify
import pyautogui
from modules.config import Config


def mousewheel():
    # 打印原始请求数据，查看其确切内容
    raw_data = request.get_data(as_text=True)  # 获取文本格式的原始数据
    # print(f"Received raw data: '{raw_data}'")
    try:
        wheel_amount = int(raw_data.strip())  # 使用strip()去除可能的前后空白字符
    except ValueError as e:
        print(f"Error converting data to int: {e}")
        return jsonify({"status": "error", "message": "Invalid data format"}), 400
    # 立方运算增加滚动的灵敏度
    wheel_amount = wheel_amount * wheel_amount * wheel_amount * wheel_amount * wheel_amount
    wheel_amount = wheel_amount * Config.MWheel_SENSITIVITY + Config.MWheel_CONSTANT
    pyautogui.scroll(wheel_amount)
    print(f"Scrolled {wheel_amount} steps")
    return jsonify({"status": "success", "steps": wheel_amount})