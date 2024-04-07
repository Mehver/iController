from flask import request, jsonify
from modules.volume import get_volume_controller


def volume_get():
    try:
        vc = get_volume_controller()
        volume = vc.get_current_volume()
        print(f"Read current volume: {volume}")
        return jsonify({"status": "success", "volume": volume})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "An error occurred while reading volume."})


def volume_set():
    vc = get_volume_controller()
    volume = request.data.decode('utf-8')
    # noinspection PyBroadException
    try:
        vc.set_volume(int(volume))
    except Exception as e:
        print(f"Invalid volume value received: {volume}")
        print(f"Exception: {e}")
        return jsonify({"status": "error", "message": "Invalid volume value."})
    print(f"Volume has been set to: {volume}")
    return jsonify({"status": "success", "message": "Volume has been set successfully."})
