from quart import request
from HostCore.infra.files.log_manager import LogManager
from HostCore.infra.files.config import Config


async def ip_log():
    ip_address = request.remote_addr
    if Config.Log.SERVER_CONNECTION_LOG:
        LogManager.log_connection(ip_address)
