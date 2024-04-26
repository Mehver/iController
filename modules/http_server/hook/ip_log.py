from quart import request
from modules.log_manager import LogManager
from modules.config import Config


async def ip_log():
    ip_address = request.remote_addr
    if Config.Log.SERVER_CONNECTION_LOG:
        LogManager.log_connection(ip_address)
