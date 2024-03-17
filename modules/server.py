from flask import Flask, request, send_from_directory, jsonify
import pyautogui
import struct
import sys
import os


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

    @app.route('/receive_coordinates', methods=['POST'])
    def receive_coordinates():
        data = request.data
        x_percentage, y_percentage = struct.unpack('<ff', data)
        if x_percentage == 0 and y_percentage == 0:
            pass
        else:
            x_move = (x_percentage / 100) * screen_width * 0.06  # SENSITIVITY 值硬编码进来了
            y_move = (y_percentage / 100) * screen_height * 0.06
            pyautogui.moveRel(x_move, y_move, duration=0.05)
        print(f"Received coordinates: x={x_percentage}%, y={y_percentage}%")
        return jsonify({"status": "success", "x": x_percentage, "y": y_percentage})

    @app.route('/button_signal', methods=['POST'])
    def button_signal():
        signal = request.data.decode('utf-8')
        if signal == 'L':
            pyautogui.click(button='left')
            action = "left click"
        elif signal == 'M':
            pyautogui.click(button='middle')
            action = "middle click"
        elif signal == 'R':
            pyautogui.click(button='right')
            action = "right click"
        elif signal == 'W':
            pyautogui.press('up')
            action = "press up"
        elif signal == 'A':
            pyautogui.press('left')
            action = "press left"
        elif signal == 'S':
            pyautogui.press('down')
            action = "press down"
        elif signal == 'D':
            pyautogui.press('right')
            action = "press right"
        else:
            return "Invalid signal", 400
        print(f"Performed {action}.")
        return jsonify({"status": "success", "action": action})

    return app
