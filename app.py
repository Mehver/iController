import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
from modules.server import server
from modules.portchecker import portchecker

print("""
 _   ___            _             _ _           
(_) / __\___  _ __ | |_ _ __ ___ | | | ___ _ __ 
| |/ /  / _ \| '_ \| __| '__/ _ \| | |/ _ \ '__|
| / /__| (_) | | | | |_| | | (_) | | |  __/ |   
|_\____/\___/|_| |_|\__|_|  \___/|_|_|\___|_|   
                                                
https://github.com/Mehver/iController
v0.5.0

""")

# PORT = 3030
while True:
    PORT = input("Give a port > ")
    try:
        PORT = int(PORT)
        if not portchecker(PORT):
            raise ValueError
    except ValueError:
        print("Invalid or unavailable port number. Please try again.")
    else:
        break

app = server()
config = Config()
config.bind = [f"0.0.0.0:{PORT}"]
asyncio.run(serve(app, config))
