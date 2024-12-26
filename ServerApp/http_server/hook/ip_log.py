from quart import request
from ServerApp.log_manager import LogManager
from ServerApp.config import Config


async def ip_log():
    ip_address = request.remote_addr
    if Config.Log.SERVER_CONNECTION_LOG:
        LogManager.log_connection(ip_address)
