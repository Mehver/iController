# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

from quart import send_from_directory


async def index(app):
    """app.route('/', methods=['GET'])(index(app))"""
    return await send_from_directory(app.static_folder, 'index.html')
