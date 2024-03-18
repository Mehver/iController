import sys
from modules.server import create_app

print("""
 _   ___            _             _ _           
(_) / __\___  _ __ | |_ _ __ ___ | | | ___ _ __ 
| |/ /  / _ \| '_ \| __| '__/ _ \| | |/ _ \ '__|
| / /__| (_) | | | | |_| | | (_) | | |  __/ |   
|_\____/\___/|_| |_|\__|_|  \___/|_|_|\___|_|   
                                                
https://github.com/Mehver/iController
v0.3.0

""")

PORT = input("Give a port > ")  # 获取用户输入的端口号
try:
    PORT = int(PORT)
except ValueError:
    print("Invalid port number.")
    sys.exit(1)

app = create_app()  # 创建Flask应用实例

if __name__ == '__main__':
    app.run(debug=False, port=PORT, host='0.0.0.0')
