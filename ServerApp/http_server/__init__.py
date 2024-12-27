from quart import Quart, send_from_directory
from ServerApp.http_server.route.dpad import dpad
from ServerApp.http_server.route.keyboard import keyboard_buttons
from ServerApp.http_server.route.keyboard import keyboard_typewriting
from ServerApp.http_server.route.keyboard import keyboard_pastetext
from ServerApp.http_server.route.system import get_system_info
from ServerApp.http_server.route.mousebutton import mousebutton
from ServerApp.http_server.route.mousewheel import mousewheel
from ServerApp.http_server.route.touchpad import touchpad
from ServerApp.http_server.route.touchpad import touchpad_reposition
from ServerApp.http_server.route.volume import volume_get
from ServerApp.http_server.route.volume import volume_set
from ServerApp.http_server.hook.ip_checker import ip_checker
from ServerApp.http_server.hook.ip_log import ip_log
from ServerApp.pyinstaller_context import PyInstallerContext


def HttpServer(static_folder) -> Quart:
    """
    Http server for iController.

    :param static_folder: The folder for static files build by React
    :return: Quart server object.
    """
    app = Quart(__name__, static_folder=PyInstallerContext().resource_path(static_folder), static_url_path='')

    app.before_request(ip_checker)
    app.before_request(ip_log)

    @app.route('/')
    async def index():
        return await send_from_directory(app.static_folder, 'index.html')
    app.route('/api/dpad', methods=['POST'])(dpad)
    app.route('/api/keyboard/buttons', methods=['POST'])(keyboard_buttons)
    app.route('/api/keyboard/typewriting', methods=['POST'])(keyboard_typewriting)
    app.route('/api/keyboard/pastetext', methods=['POST'])(keyboard_pastetext)
    app.route('/api/system/info', methods=['GET'])(get_system_info)
    app.route('/api/mousebutton', methods=['POST'])(mousebutton)
    app.route('/api/mousewheel', methods=['POST'])(mousewheel)
    app.route('/api/touchpad', methods=['POST'])(touchpad)
    app.route('/api/touchpad/reposition', methods=['POST'])(touchpad_reposition)
    app.route('/api/volume/get', methods=['GET'])(volume_get)
    app.route('/api/volume/set', methods=['POST'])(volume_set)

    return app
