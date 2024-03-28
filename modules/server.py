from flask import Flask, request, send_from_directory, jsonify
import pyautogui
import struct
import sys
import os
from modules.config import Config


# 动态确定配置文件和静态文件夹路径
def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        # 如果是exe文件，使用exe所在目录
        base_path = sys._MEIPASS
    else:
        # 否则使用脚本所在目录
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# 创建 Flask 应用实例的函数
def create_app(static_folder='build', static_url_path=''):
    app = Flask(__name__, static_folder=get_resource_path(static_folder), static_url_path=static_url_path)

    # 获取屏幕尺寸
    screen_width, screen_height = pyautogui.size()

    @app.route('/')
    def serve():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/api/dpad', methods=['POST'])
    def dpad():
        signal = request.data.decode('utf-8')
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
        print(f"Performed {action}.")
        return jsonify({"status": "success", "action": action})

    @app.route('/api/mousebutton', methods=['POST'])
    def mousebutton():
        signal = request.data.decode('utf-8')
        if signal == 'Left':
            pyautogui.click(button='left')
            action = "left click"
        elif signal == 'Middle':
            pyautogui.click(button='middle')
            action = "middle click"
        elif signal == 'Right':
            pyautogui.click(button='right')
            action = "right click"
        else:
            return "Invalid signal", 400
        print(f"Performed {action}.")
        return jsonify({"status": "success", "action": action})

    @app.route('/api/mousewheel', methods=['POST'])
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

    @app.route('/api/touchpad', methods=['POST'])
    def touchpad():
        data = request.data
        x_percentage, y_percentage = struct.unpack('<ff', data)
        if x_percentage == 0 and y_percentage == 0:
            pass
        else:
            x_move = (x_percentage / 100.0) * screen_width * Config.TPad_SENSITIVITY * 0.06
            y_move = (y_percentage / 100.0) * screen_height * Config.TPad_SENSITIVITY * 0.06
            pyautogui.moveRel(x_move, y_move, duration=0.05)
        print(f"Received coordinates: x={x_percentage}%, y={y_percentage}%")
        return jsonify({"status": "success", "x": x_percentage, "y": y_percentage})

    return app
