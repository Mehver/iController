import asyncio
from hypercorn.config import Config as HypercornConfig
from hypercorn.asyncio import serve
from HostCore.http_server import HttpServer
from HostCore.infra.files.config import Config
from HostCore.utils.pyinstaller_context import PyInstallerContext
from HostDesktopCLI.get_address import get_address
from HostDesktopCLI.cli_logo import cli_logo
from HostDesktopCLI.cli_qrcode import url_to_qrcode_print

def HostDesktopCLI(version='dev'):
    print(cli_logo(version))
    Config.init()
    static_folder = PyInstallerContext().frontend_resource_path()
    app = HttpServer(static_folder)
    host_ip_address = get_address()
    url_to_qrcode_print(host_ip_address)
    hypercorn_config = HypercornConfig()
    hypercorn_config.bind = [host_ip_address]
    asyncio.run(serve(app, hypercorn_config))
