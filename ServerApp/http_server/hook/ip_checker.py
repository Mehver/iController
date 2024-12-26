from quart import request, abort
from ServerApp.config import Config


async def ip_checker():
    """
    app.before_request(ip_checker)
    """
    client_ip = request.remote_addr
    # print(f"Connection from \"{client_ip}\".")
    if Config.HttpServer.IP_CHECK_MODE == "blacklist":
        # print("Server running in blacklist mode.")
        # print(f"Blacklist: {Config.HttpServer.IP_BLACKLIST}")
        if client_ip in Config.HttpServer.IP_BLACKLIST:
            abort(403)
    elif Config.HttpServer.IP_CHECK_MODE == "whitelist":
        # print("Server running in whitelist mode.")
        # print(f"Whitelist: {Config.HttpServer.IP_WHITELIST}")
        if client_ip not in Config.HttpServer.IP_WHITELIST:
            abort(403)
    else:
        print("Invalid IP check mode, please check the configuration file.")
        abort(500)
