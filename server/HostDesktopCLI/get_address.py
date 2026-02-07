import ipaddress
from HostCore.infra.files.config import Config
from HostCore.utils.check_ip import check_ip
from HostCore.utils.check_port import check_port


def get_address():
    HOST = Config.HttpServer.HOST
    PORT = Config.HttpServer.PORT

    try:
        local_ip = check_ip()
    except Exception:
    # except Exception as e:
        # print(f"[DEBUG] get_address {e}")
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
            print("Invalid selection. Please enter 1, 2, 3, or 4.")
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
            print("Invalid selection. Please enter 1, 2 or 3.")

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
    if choice == "2" or choice == "3" or choice == "4":
        overwrite = input(
            f"Do you want to overwrite the configuration file with this IP? (y/N) > "
        ).strip()
        if overwrite.lower() == "y":
            Config.HttpServer.HOST = HOST
            Config.save()

    print()

    try:
        if not 0 < PORT < 65535:
            raise ValueError
        if not check_port(PORT):
            raise IndexError
        use = input(f"Do you want to use the port [:{PORT}] given by the configuration file? (Y/n) > ")
        if use.lower() != 'n':
            print(f"Web server will runs on [{HOST}:{PORT}].")
            return f"{HOST}:{PORT}"
    except ValueError:
        print(f"The port [{PORT}] in the configuration file is not a valid port number,")
        print("you need to specify a new port.")
    except IndexError:
        print(f"The port [{PORT}] in the configuration file is already in use by another program.")
        force = input("Do you want to force the use of this port? (y/N) > ")
        if force.lower() == 'y':
            print(f"Web server will runs on [{HOST}:{PORT}].\n")
            return f"{HOST}:{PORT}"
    while True:
        PORT = input("Give a port > ")
        try:
            PORT = int(PORT)
            if not 0 < PORT < 65535:
                raise ValueError
            if not check_port(PORT):
                raise IndexError
        except ValueError:
            print("Port number must be an integer between 1 and 65534.")
        except IndexError:
            print("This port is already in use by another program.")
            force = input("Do you want to force the use of this port? (y/N) > ")
            if force.lower() == 'y':
                print(f"Web server will runs on [{HOST}:{PORT}].\n")
                return f"{HOST}:{PORT}"
        else:
            break
    update = input("Do you want to update the configuration file with this port? (y/N) > ")
    if update.lower() == 'y':
        Config.HttpServer.PORT = PORT
        Config.save()
    print(f"Web server will runs on [{HOST}:{PORT}].\n")
    return f"{HOST}:{PORT}"

