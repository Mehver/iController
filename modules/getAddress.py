import socket
import platform
from modules.config import Config


def portChecker(port):
    """
    检查端口是否可用。
    - 如果端口是一个数字且在合法范围内（1-65534）
    - 并且没有被别的程序使用，则返回True。
    """
    os_name = platform.system()
    if os_name == 'Windows':
        # Windows下使用psutil检查
        import psutil
        if isinstance(port, int) and 0 < port < 65535:
            connections = psutil.net_connections()
            for conn in connections:
                if conn.laddr.port == port:
                    return False  # 端口已被占用
            return True  # 端口未被占用，可用
        else:
            return False  # 端口号不合法
    elif os_name == 'Darwin':
        # MacOS下使用socket尝试绑定端口检查
        if isinstance(port, int) and 0 < port < 65535:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('localhost', port))
                    return True  # 端口未被占用，可用
                except socket.error:
                    return False  # 端口已被占用
        else:
            return False  # 端口号不合法
    else:
        raise NotImplementedError("This OS is not supported.")


def getAddress():
    PORT = Config.HttpServer.PORT
    try:
        if not 0 < PORT < 65535:
            raise ValueError
        if not portChecker(PORT):
            raise IndexError
        print(f"Do you want to use the port [{PORT}] given by the configuration file?")
        use = input("Use this port? (Y/n) > ")
        if use != 'n' and use != 'N':
            return f"{Config.HttpServer.HOST}:{PORT}"
    except ValueError:
        print(f"The port [{PORT}] in the configuration file is not a valid port number.")
    except IndexError:
        print(f"The port [{PORT}] in the configuration file is already in use by another program.")
        force = input("Do you want to force the use of this port? (y/N) > ")
        if force == 'y' or force == 'Y':
            return f"{Config.HttpServer.HOST}:{PORT}"
    while True:
        PORT = input("Give a port > ")
        try:
            PORT = int(PORT)
            if not 0 < PORT < 65535:
                raise ValueError
            if not portChecker(PORT):
                raise IndexError
        except ValueError:
            print("Port number must be an integer between 1 and 65534.")
        except IndexError:
            print("This port is already in use by another program.")
            force = input("Do you want to force the use of this port? (y/N) > ")
            if force == 'y' or force == 'Y':
                break
        else:
            break
    update = input("Do you want to update the configuration file with this port? (Y/n) > ")
    if update != 'n' and update != 'N':
        Config.HttpServer.PORT = PORT
        Config.save()
    return f"{Config.HttpServer.HOST}:{PORT}"
