from quart import request
from HostCore.infra.files.log_manager import LogManager


async def ip_log():
    ip_address = request.remote_addr
    LogManager.log_connection(ip_address)
