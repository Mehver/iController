from quart import jsonify, request
import pyautogui
import pyperclip
import platform
from HostCore.utils.log_manager import LogManager


async def keyboard_buttons():
    """app.route('/api/keyboard/buttons', methods=['POST'])(keyboard_buttons)"""
    signal = (await request.get_data()).decode('utf-8')
    if signal == 'Backspace':
        pyautogui.press('backspace')
        action = "press backspace"
    elif signal == 'Enter':
        pyautogui.press('enter')
        action = "press enter"
    else:
        return "Invalid signal", 400
    LogManager.log_console(f"Keyboard performed {action}.")
    return jsonify({"status": "success", "action": action})


async def keyboard_typewriting():
    """app.route('/api/keyboard/typewriting', methods=['POST'])(keyboard_typewriting)"""
    text = (await request.get_data()).decode('utf-8')
    try:
        pyautogui.write(text, interval=0.05)
        LogManager.log_console(f"Keyboard typewriting: \"{text}\".")
        return jsonify({"status": "success", "message": "Text has been sent successfully."})
    except Exception as e:
        LogManager.log_console(f"Keyboard typewriting error: {e}.")
        return jsonify({"status": "error", "message": "An error occurred while sending text."}), 500


async def keyboard_pastetext():
    """app.route('/api/keyboard/pastetext', methods=['POST'])(keyboard_pastetext)"""
    text = (await request.get_data()).decode('utf-8')
    os_name = platform.system()
    if os_name == 'Windows':
        try:
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            LogManager.log_console(f"Keyboard paste text: \"{text}\".")
            return jsonify({"status": "success", "message": "Text has been pasted successfully."})
        except Exception as e:
            LogManager.log_console(f"Keyboard paste text error: {e}.")
            return jsonify({"status": "error", "message": "An error occurred while pasting text."}), 500
    elif os_name == 'Darwin':
        try:
            pyautogui.write(text, interval=0.05)
            return jsonify({"status": "success", "message": "Text has been sent successfully."})
        except Exception as e:
            LogManager.log_console(f"Keyboard paste text error: {e}.")
            return jsonify({"status": "error", "message": "An error occurred while sending text."}), 500
