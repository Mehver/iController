import socket
import platform

def portchecker(port):
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
        raise NotImplementedError("This OS is not supported for port checking")
