from quart import request, jsonify
from HostCore.volume_controller import get_volume_controller
from HostCore.log_manager import LogManager


async def volume_get():
    """app.route('/api/volume/get', methods=['GET'])(volume_get)"""
    try:
        vc = get_volume_controller()
        volume = vc.get_current_volume()
        LogManager.log_console(f"Volume obtain: {int(volume)}.")
        return jsonify({"status": "success", "volume": volume})
    except Exception as e:
        LogManager.log_console(f"Error: {e}.")
        return jsonify({"status": "error", "message": f"An error ({e}) occurred while reading volume."})


async def volume_set():
    """app.route('/api/volume/set', methods=['POST'])(volume_set)"""
    volume = "Failed to get volume."
    try:
        vc = get_volume_controller()
        volume = (await request.get_data()).decode('utf-8')
        vc.set_volume(int(volume))
        LogManager.log_console(f"Volume set to: {volume}.")
        return jsonify({"status": "success", "message": "Volume has been set successfully."})
    except Exception as e:
        LogManager.log_console(f"Invalid volume value received: {volume}.")
        LogManager.log_console(f"Exception: {e}.")
        return jsonify({"status": "error", "message": "Invalid volume value."})
