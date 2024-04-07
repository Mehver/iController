from flask import request, jsonify
import pyautogui
import pyperclip
import platform


def keyboard_buttons():
    signal = request.data.decode('utf-8')
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


def keyboard_typewriting():
    text = request.data.decode('utf-8')  # 获取请求体中的文本内容
    try:
        pyautogui.write(text, interval=0.05)  # 将文本输入到当前聚焦的位置
        return jsonify({"status": "success", "message": "Text has been sent successfully."})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "An error occurred while sending text."}), 500


def keyboard_pastetext():
    text = request.data.decode('utf-8')  # 获取请求体中的文本内容
    os_name = platform.system()
    if os_name == 'Windows':
        try:
            pyperclip.copy(text)  # 将文本复制到剪贴板
            pyautogui.hotkey('ctrl', 'v')  # 模拟按下粘贴快捷键（Windows/Linux）
            # 对于macOS，使用 pyautogui.hotkey('cmd', 'v')
            return jsonify({"status": "success", "message": "Text has been pasted successfully."})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"status": "error", "message": "An error occurred while pasting text."}), 500
    elif os_name == 'Darwin':
        try:
            pyautogui.write(text, interval=0.05)  # 将文本输入到当前聚焦的位置
            return jsonify({"status": "success", "message": "Text has been sent successfully."})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"status": "error", "message": "An error occurred while sending text."}), 500
