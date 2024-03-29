from flask import Flask, send_from_directory
import sys
import os
from modules.server.dpad import dpad
from modules.server.mousebutton import mousebutton
from modules.server.mousewheel import mousewheel
from modules.server.touchpad import touchpad


# 动态确定配置文件和静态文件夹路径
def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        # 如果是exe文件，使用exe所在目录
        # noinspection PyProtectedMember
        base_path = sys._MEIPASS
    else:
        # 否则使用脚本所在目录
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# 创建 Flask 应用实例的函数
def server(static_folder='build', static_url_path=''):
    app = Flask(__name__, static_folder=get_resource_path(static_folder), static_url_path=static_url_path)

    def serve():
        return send_from_directory(app.static_folder, 'index.html')

    app.route('/')(serve)
    app.route('/api/dpad', methods=['POST'])(dpad)
    app.route('/api/mousebutton', methods=['POST'])(mousebutton)
    app.route('/api/mousewheel', methods=['POST'])(mousewheel)
    app.route('/api/touchpad', methods=['POST'])(touchpad)

    return app
