from quart import request, jsonify
from modules.volumeController import get_volume_controller


async def volume_get():
    try:
        vc = get_volume_controller()
        volume = vc.get_current_volume()
        print(f"Volume obtain: {int(volume)}.")
        return jsonify({"status": "success", "volume": volume})
    except Exception as e:
        print(f"Error: {e}.")
        return jsonify({"status": "error", "message": f"An error ({e}) occurred while reading volume."})


async def volume_set():
    volume = "Failed to get volume."
    try:
        vc = get_volume_controller()
        volume = (await request.get_data()).decode('utf-8')
        vc.set_volume(int(volume))
        print(f"Volume set to: {volume}.")
        return jsonify({"status": "success", "message": "Volume has been set successfully."})
    except Exception as e:
        print(f"Invalid volume value received: {volume}.")
        print(f"Exception: {e}.")
        return jsonify({"status": "error", "message": "Invalid volume value."})
