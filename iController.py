VERSION = "v0.7.2"

from HostCore.utils.pyinstaller_context import PyInstallerContext

def run_cli():
    try:
        from HostDesktopCLI import HostDesktopCLI
        HostDesktopCLI(VERSION)
    except ImportError:
        print("【Error】 Cannot import HostDesktopCLI")

def run_gui():
    try:
        from HostDesktopGUI import HostDesktopGUI
        HostDesktopGUI(VERSION)
    except ImportError:
        print("【Error】 Cannot import HostDesktopGUI")

def main():
    if PyInstallerContext().check_build():
        if PyInstallerContext().is_cli():
            run_cli()
        elif PyInstallerContext().is_gui():
            run_gui()
    else:
        print("This program is not built but in dev mode.")
        print("Two options are available:")
        print("【1】 Run CLI version")
        print("【2】 Run GUI version")
        while True:
            choice = (input("Select 1/2 (default: 1) > ").strip() or "1")
            if choice in {"1", "2"}:
                break
            print("Invalid selection. Please enter 1 or 2.")
        if choice == "1":
            run_cli()
        elif choice == "2":
            run_gui()

if __name__ == "__main__":
    main()
