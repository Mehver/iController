import socket
import ipaddress

def find_local_ip(target=("8.8.8.8", 80)) -> str | None:
    """
    返回用于到达 target 的本机IPv4地址（通常是当前默认出站网卡的LAN IP）。
    不保证 target 可达，但会触发路由选择。
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(target)
        ip = s.getsockname()[0]
        # 过滤不想要的
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast:
            return None
        return ip
    except OSError:
        return None
    finally:
        s.close()