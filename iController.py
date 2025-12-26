VERSION = "v0.6.6"

import asyncio
from hypercorn.config import Config as HypercornConfig
from hypercorn.asyncio import serve
from HostCore.http_server import HttpServer
from HostCore.utils.config import Config
from HostCore.pyinstaller_context import PyInstallerContext
from HostDesktopCLI.get_address import get_address

print(f"""
 _   ___            _             _ _           
(_) / __\\___  _ __ | |_ _ __ ___ | | | ___ _ __ 
| |/ /  / _ \\| '_ \\| __| '__/ _ \\| | |/ _ \\ '__|
| / /__| (_) | | | | |_| | | (_) | | |  __/ |   
|_\\____/\\___/|_| |_|\\__|_|  \\___/|_|_|\\___|_|   
                                                
https://github.com/Mehver/iController
{VERSION}

""")

Config.init()
static_folder = PyInstallerContext().resource_path("ClientBrowserUI/build")
app = HttpServer(static_folder)
config = HypercornConfig()
config.bind = [get_address()]
asyncio.run(serve(app, config))
