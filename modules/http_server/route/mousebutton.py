from quart import request, jsonify
import pyautogui


async def mousebutton():
    """
    app.route('/api/mousebutton', methods=['POST'])(mousebutton)
    """
    signal = (await request.get_data()).decode('utf-8')
    if signal == 'Left':
        pyautogui.click(button='left')
        action = "left click"
    elif signal == 'Middle':
        pyautogui.click(button='middle')
        action = "middle click"
    elif signal == 'Right':
        pyautogui.click(button='right')
        action = "right click"
    else:
        return "Invalid signal", 400
    print(f"Mouse performed {action}.")
    return jsonify({"status": "success", "action": action})
