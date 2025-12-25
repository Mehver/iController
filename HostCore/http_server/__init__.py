from quart import Quart, send_from_directory
from HostCore.http_server.route.dpad import dpad
from HostCore.http_server.route.keyboard import keyboard_buttons
from HostCore.http_server.route.keyboard import keyboard_typewriting
from HostCore.http_server.route.keyboard import keyboard_pastetext
from HostCore.http_server.route.system import get_system_info
from HostCore.http_server.route.mousebutton import mousebutton
from HostCore.http_server.route.mousewheel import mousewheel
from HostCore.http_server.route.touchpad import touchpad
from HostCore.http_server.route.touchpad import touchpad_reposition
from HostCore.http_server.route.volume import volume_get
from HostCore.http_server.route.volume import volume_set
from HostCore.http_server.hook.ip_checker import ip_checker
from HostCore.http_server.hook.ip_log import ip_log


def HttpServer(static_folder) -> Quart:
    """
    Http server for iController.

    :param static_folder: The folder for static files build by React
    :return: Quart server object.
    """
    app = Quart(__name__, static_folder=static_folder, static_url_path='')

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
