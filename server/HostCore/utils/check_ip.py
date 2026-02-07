import socket
import ipaddress
import psutil
from HostCore.utils.check_platform import get_platform

def check_ip() -> str | None:
    os_name = get_platform()
    if os_name == 'Windows':
        return outbound_ip()
    elif os_name == 'Darwin':
        return physical_ip()
    else:
        raise NotImplementedError(f"This OS ({os_name}) is not supported.")


def outbound_ip(target=("8.8.8.8", 80)):
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


def physical_ip() -> str | None:
    """
    在 mac / Linux 上优先返回物理网卡（如 en0）的 IPv4 地址。
    过滤 lo、utun、vmnet、vboxnet 等常见虚拟接口。
    """
    bad_prefixes = (
        "lo",  # loopback
        "utun",  # macOS VPN/Tunnel
        "tap", "tun",
        "vmnet",  # VMWare
        "vboxnet",  # VirtualBox
        "awdl",  # Apple 无线直连
        "llw",
        "ppp",
        "gif", "stf",
    )
    prefer_prefixes = (
        "en",  # macOS 有线 / Wi-Fi 通常是 en0/en1
        "eth",  # Linux 有线
        "wlan", "wl",  # Linux 无线
    )

    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    candidates: list[tuple[int, str, str]] = []  # (score, ifname, ip)

    for ifname, addr_list in addrs.items():
        st = stats.get(ifname)
        if not st or not st.isup:
            continue

        # 过滤明显虚拟 / 不想要的接口名
        if ifname.startswith(bad_prefixes):
            continue

        for a in addr_list:
            if a.family != socket.AF_INET:
                continue

            ip = a.address
            ip_obj = ipaddress.ip_address(ip)

            # 只考虑非环回、非 link-local 的 IPv4，一般还希望是私网地址
            if ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast:
                continue
            # 如果你只想 LAN，可以限制为私有地址
            if not ip_obj.is_private:
                continue

            score = 0
            # 优先 en0 / en1 / eth0 等
            if ifname.startswith(prefer_prefixes):
                score += 10
            if ifname == "en0":
                score += 5  # mac 上 en0 通常是主网口

            candidates.append((score, ifname, ip))

    if not candidates:
        return None

    # 分数高的优先
    candidates.sort(reverse=True)
    return candidates[0][2]