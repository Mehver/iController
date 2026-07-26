# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

from quart import request
from HostCore.infra.files.log_manager import LogManager


async def ip_log():
    ip_address = request.remote_addr
    LogManager.log_connection(ip_address)
