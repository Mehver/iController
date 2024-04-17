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

    def resource_path(self, relative_path):
        # 获取资源的绝对路径
        if self.bundled:
            # noinspection PyProtectedMember
            # noinspection PyUnresolvedReferences
            base_path = sys._MEIPASS
        else:
            # 否则，使用当前文件的目录作为基准路径
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def check_environment(self):
        # 提供一个检查当前运行环境的方法
        if self.bundled:
            print("运行在打包环境下")
            return "pyinstaller"
        else:
            print("运行在开发环境下")
            return "dev"
