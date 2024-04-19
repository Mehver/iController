import asyncio
from hypercorn.config import Config as HypercornConfig
from hypercorn.asyncio import serve
from modules.http_server import HttpServer
from modules.get_address import get_address
from modules.config import Config

print("""
 _   ___            _             _ _           
(_) / __\___  _ __ | |_ _ __ ___ | | | ___ _ __ 
| |/ /  / _ \| '_ \| __| '__/ _ \| | |/ _ \ '__|
| / /__| (_) | | | | |_| | | (_) | | |  __/ |   
|_\____/\___/|_| |_|\__|_|  \___/|_|_|\___|_|   
                                                
https://github.com/Mehver/iController
v0.6.1

""")

Config.init()
app = HttpServer()
config = HypercornConfig()
config.bind = [get_address()]
asyncio.run(serve(app, config))
