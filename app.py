import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
from modules.httpServer import httpServer
from modules.getAddress import getAddress

print("""
 _   ___            _             _ _           
(_) / __\___  _ __ | |_ _ __ ___ | | | ___ _ __ 
| |/ /  / _ \| '_ \| __| '__/ _ \| | |/ _ \ '__|
| / /__| (_) | | | | |_| | | (_) | | |  __/ |   
|_\____/\___/|_| |_|\__|_|  \___/|_|_|\___|_|   
                                                
https://github.com/Mehver/iController
v0.5.0

""")

app = httpServer()
config = Config()
config.bind = [getAddress()]
asyncio.run(serve(app, config))
