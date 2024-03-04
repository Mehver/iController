import yaml
import struct
from flask import Flask, request, send_from_directory, jsonify
import pyautogui

# 默认配置
CONFIG_PATH = "./config.yaml"

# 读取配置文件
with open(CONFIG_PATH, "r") as stream:
    config = yaml.safe_load(stream)

PORT = config['port']
SENSITIVITY = config.get('sensitivity', 1)  # 如果没有设置灵敏度，则默认为1

app = Flask(__name__, static_folder='build', static_url_path='')

# 获取屏幕尺寸
screen_width, screen_height = pyautogui.size()


@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/receive_coordinates', methods=['POST'])
def receive_coordinates():
    # 读取请求的二进制数据
    data = request.data

    # 解码二进制数据，得到x和y的值
    # 使用小端序解码
    x_percentage, y_percentage = struct.unpack('<ff', data)

    # 如果接收到的是0,0，则不移动鼠标
    if x_percentage == 0 and y_percentage == 0:
        pass
    else:
        # 计算鼠标应该移动的距离
        x_move = (x_percentage / 100) * screen_width * SENSITIVITY
        y_move = (y_percentage / 100) * screen_height * SENSITIVITY

        # 移动鼠标
        pyautogui.moveRel(x_move, y_move, duration=0.05)

    print(f"Received coordinates: x={x_percentage}%, y={y_percentage}%")
    return jsonify({"status": "success", "x": x_percentage, "y": y_percentage})


if __name__ == '__main__':
    print("""
 _   ___            _             _ _           
(_) / __\___  _ __ | |_ _ __ ___ | | | ___ _ __ 
| |/ /  / _ \| '_ \| __| '__/ _ \| | |/ _ \ '__|
| / /__| (_) | | | | |_| | | (_) | | |  __/ |   
|_\____/\___/|_| |_|\__|_|  \___/|_|_|\___|_|   
                                                

    """)

    pyautogui.FAILSAFE = False  # 禁用pyautogui的自动防故障机制
    app.run(debug=True, port=PORT, host='0.0.0.0')
