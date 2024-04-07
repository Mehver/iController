import psutil


def portchecker(port):
    """
    使用psutil检查端口是否可用
    - 如果端口是一个数字且在合法范围内（1-65534）
    - 并且没有被别的程序使用，则返回True
    """
    # 确保端口号是整数且在合法范围内
    if isinstance(port, int) and 0 < port < 65535:
        # 获取当前所有的网络连接
        connections = psutil.net_connections()
        # 遍历所有连接，检查端口是否被占用
        for conn in connections:
            if conn.laddr.port == port:
                return False  # 端口已被占用
        return True  # 端口未被占用，可用
    else:
        return False  # 端口号不合法
