from quart import jsonify, request
import pyautogui
import pyperclip
import platform


async def keyboard_buttons():
    signal = (await request.get_data()).decode('utf-8')
    if signal == 'Backspace':
        pyautogui.press('backspace')
        action = "press backspace"
    elif signal == 'Enter':
        pyautogui.press('enter')
        action = "press enter"
    else:
        return "Invalid signal", 400
    print(f"Performed {action}.")
    return jsonify({"status": "success", "action": action})


async def keyboard_typewriting():
    text = (await request.get_data()).decode('utf-8')
    try:
        pyautogui.write(text, interval=0.05)
        return jsonify({"status": "success", "message": "Text has been sent successfully."})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "An error occurred while sending text."}), 500


async def keyboard_pastetext():
    text = (await request.get_data()).decode('utf-8')
    os_name = platform.system()
    if os_name == 'Windows':
        try:
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            return jsonify({"status": "success", "message": "Text has been pasted successfully."})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"status": "error", "message": "An error occurred while pasting text."}), 500
    elif os_name == 'Darwin':
        try:
            pyautogui.write(text, interval=0.05)
            return jsonify({"status": "success", "message": "Text has been sent successfully."})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"status": "error", "message": "An error occurred while sending text."}), 500
