import socket
import platform
import ipaddress
from HostCore.utils.config import Config


def port_checker(port):
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


def get_address():
    HOST = Config.HttpServer.HOST
    PORT = Config.HttpServer.PORT

    try:
        local_ip = pick_local_ip_via_route()
    except:
        local_ip = None

    print(f"Your current Host IP provide by configuration file is [{HOST}].")
    print("How do you want to bind the web server host?")
    if local_ip:
        print(f"【1】 Use the IP provide by configuration file [{HOST}]")
        print(f"【2】 Use detected local IP [{local_ip}]")
        print(f"【3】 Use [0.0.0.0] (listen on all interfaces / 'broadcast')")
        print(f"【4】 Enter an IP address manually")
        while True:
            choice = (input("Select 1/2/3/4 (default: 1) > ").strip() or "1")
            if choice in {"1", "2", "3", "4"}:
                break
            print("Invalid selection. Please enter 1, 2, or 3.")
    else:
        print(f"【1】 Use the IP provide by configuration file [{HOST}]")
        print(f"【2】 Use [0.0.0.0] (listen on all interfaces / 'broadcast')")
        print(f"【3】 Enter an IP address manually")
        while True:
            choice = (input("Select 1/2/3 (default: 1) > ").strip() or "1")
            if choice == "1":
                break
            elif choice in {"2", "3"}:
                choice = f"{int(choice) + 1}"
                break
            print("Invalid selection. Please enter 1 or 2.")

    if choice == "1":
        pass
    elif choice == "2":
        HOST = local_ip
    elif choice == "3":
        HOST = '0.0.0.0'
    elif choice == "4":
        while True:
            manual = input(
                "Enter the host IPv4 address to bind to (e.g., [127.0.0.1] or [192.168.1.50]) > "
            ).strip().replace("[", "").replace("]", "")
            try:
                ip_obj = ipaddress.ip_address(manual)
                if ip_obj.version != 4:
                    raise ValueError
                if ip_obj.is_multicast:
                    print("Multicast addresses are not valid for binding.")
                    continue
            except ValueError:
                print("Invalid IPv4 address. Please try again.")
                continue
            HOST = manual
            break
    if choice == "2" or choice == "4":
        overwrite = input(
            f"Do you want to overwrite the configuration file with this IP? (y/N) > "
        ).strip()
        if overwrite.lower() == "y":
            Config.HttpServer.HOST = HOST
            Config.save()

    try:
        if not 0 < PORT < 65535:
            raise ValueError
        if not port_checker(PORT):
            raise IndexError
        use = input(f"Do you want to use the port [:{PORT}] given by the configuration file? (Y/n) > ")
        if use.lower() != 'n':
            print(f"Web server will runs on [{HOST}:{PORT}].")
            return f"{HOST}:{PORT}"
    except ValueError:
        print(f"The port [{PORT}] in the configuration file is not a valid port number.")
    except IndexError:
        print(f"The port [{PORT}] in the configuration file is already in use by another program.")
        force = input("Do you want to force the use of this port? (y/N) > ")
        if force.lower() == 'y':
            print(f"Web server will runs on [{HOST}:{PORT}].")
            return f"{HOST}:{PORT}"
    while True:
        PORT = input("Give a port > ")
        try:
            PORT = int(PORT)
            if not 0 < PORT < 65535:
                raise ValueError
            if not port_checker(PORT):
                raise IndexError
        except ValueError:
            print("Port number must be an integer between 1 and 65534.")
        except IndexError:
            print("This port is already in use by another program.")
            force = input("Do you want to force the use of this port? (y/N) > ")
            if force.lower() == 'y':
                print(f"Web server will runs on [{HOST}:{PORT}].")
                return f"{HOST}:{PORT}"
        else:
            break
    update = input("Do you want to update the configuration file with this port? (y/N) > ")
    if update.lower() == 'y':
        Config.HttpServer.PORT = PORT
        Config.save()
    print(f"Web server will runs on [{HOST}:{PORT}].")
    return f"{HOST}:{PORT}"


def pick_local_ip_via_route(target=("8.8.8.8", 80)) -> str | None:
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
