from quart import send_from_directory


async def index(app):
    """app.route('/', methods=['GET'])(index(app))"""
    return await send_from_directory(app.static_folder, 'index.html')
