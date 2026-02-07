import sys
import os


class PyInstallerContext:
    """
    # 使用示例
    if __name__ == "__main__":
        context = PyInstallerContext()
        context.check_environment()
        # 例如获取一个图标文件的路径
        icon_path = context.resource_path('icons/app_icon.png')
        print(f"Icon path: {icon_path}")
    """
    def __init__(self):
        # 检测是否是 PyInstaller 打包的环境
        self.bundled = getattr(sys, 'frozen', False)
        self.mode = "cli"
        # HACK: Detect GUI bundle via PySide6 presence.
        # WARNING: Relies on packaging assumption (CLI excludes Qt).
        try:
            from PySide6.QtCore import QObject
            self.mode = "gui"
        except ImportError:
            self.mode = "cli"

    def frontend_resource_path(self):
        # 获取资源的绝对路径
        if self.bundled:
            # noinspection PyProtectedMember
            # noinspection PyUnresolvedReferences
            base_path = sys._MEIPASS
        else:
            # 否则，使用当前文件的目录作为基准路径
            base_path = os.path.abspath(os.path.dirname(__file__))
            base_path = os.path.abspath(os.path.join(base_path, ".."))
        return os.path.join(base_path, "./frontend/build")

    def check_build(self):
        if self.bundled:
            return True
        return False

    def is_cli(self) -> bool:
        return self.mode == "cli"

    def is_gui(self) -> bool:
        return self.mode == "gui"