# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

import asyncio

from quart import request, jsonify

from HostCore.brightness_controller import get_brightness_controller
from HostCore.brightness_controller.base import BrightnessUnsupportedError
from HostCore.infra.files.log_manager import LogManager


async def brightness_get():
    """app.route('/api/brightness/get', methods=['GET'])(brightness_get)"""
    try:
        brightness_controller = get_brightness_controller()
        if brightness_controller is None:
            return jsonify({
                "status": "success", "brightness": 0,
                "message": "Brightness control ignored."
            })
        brightness = await asyncio.to_thread(
            brightness_controller.get_current_brightness
        )
        LogManager.log_console(f"Brightness obtain: {brightness}.")
        return jsonify({"status": "success", "brightness": brightness})
    except BrightnessUnsupportedError:
        LogManager.log_console("Brightness control is not supported on this device.")
        return jsonify({
            "status": "error",
            "message": "Brightness control is not supported on this device."
        })
    except Exception as error:
        LogManager.log_console(f"Brightness control error: {error}.")
        return jsonify({
            "status": "error",
            "message": f"An error ({error}) occurred while reading brightness."
        })


async def brightness_set():
    """app.route('/api/brightness/set', methods=['POST'])(brightness_set)"""
    brightness = "Failed to get brightness."
    try:
        brightness = (await request.get_data()).decode('utf-8')
        brightness_value = int(brightness)
        if not 0 <= brightness_value <= 100:
            raise ValueError("Brightness must be between 0 and 100.")
    except (UnicodeDecodeError, ValueError) as error:
        LogManager.log_console(f"Invalid brightness value received: {brightness}.")
        LogManager.log_console(f"Exception: {error}.")
        return jsonify({"status": "error", "message": "Invalid brightness value."})

    try:
        brightness_controller = get_brightness_controller()
        if brightness_controller is None:
            return jsonify({
                "status": "success", "message": "Brightness control ignored."
            })
        await asyncio.to_thread(brightness_controller.set_brightness, brightness_value)
        LogManager.log_console(f"Brightness set to: {brightness_value}.")
        return jsonify({
            "status": "success", "message": "Brightness has been set successfully."
        })
    except BrightnessUnsupportedError:
        LogManager.log_console("Brightness control is not supported on this device.")
        return jsonify({
            "status": "error",
            "message": "Brightness control is not supported on this device."
        })
    except Exception as error:
        LogManager.log_console(f"Brightness control error: {error}.")
        return jsonify({
            "status": "error",
            "message": f"An error ({error}) occurred while setting brightness."
        })
