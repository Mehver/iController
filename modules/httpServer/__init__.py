from quart import Quart, send_from_directory
from modules.httpServer.dpad import dpad
from modules.httpServer.keyboard import keyboard_buttons
from modules.httpServer.keyboard import keyboard_typewriting
from modules.httpServer.keyboard import keyboard_pastetext
from modules.httpServer.system import get_system_info
from modules.httpServer.mousebutton import mousebutton
from modules.httpServer.mousewheel import mousewheel
from modules.httpServer.touchpad import touchpad
from modules.httpServer.touchpad import touchpad_reposition
from modules.httpServer.volume import volume_get
from modules.httpServer.volume import volume_set
from modules.pyinstallerContext import PyInstallerContext


def httpServer(static_folder='build', static_url_path=''):
    pyinstallerContext = PyInstallerContext()
    app = Quart(__name__, static_folder=pyinstallerContext.resource_path(static_folder), static_url_path=static_url_path)

    async def index():
        return await send_from_directory(app.static_folder, 'index.html')

    app.route('/')(index)
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
