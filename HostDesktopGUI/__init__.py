import sys
import builtins

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from HostDesktopGUI.gui_config import APP_NAME, APP_ICON_PATH
from HostDesktopGUI.main_window import ShellWindow, gui_input


# 保持一个全局引用，防止窗口被 GC
_window_ref = None


def HostDesktopGUI(version: str = "dev"):
    """
    GUI 入口：在 iController 里用户选择 2 时调用：
        from HostDesktopGUI import HostDesktopGUI
        HostDesktopGUI("dev")
    """

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    # 应用级图标（任务栏 / 对话框等）
    if APP_ICON_PATH.is_file():
        app.setWindowIcon(QIcon(str(APP_ICON_PATH)))

    # 把全局 input() 替换为 GUI 版本
    # 后面 CLI 代码里只要调用 input()，就会从这个 GUI 读数据
    builtins.input = gui_input

    global _window_ref
    _window_ref = ShellWindow(version)
    _window_ref.resize(980, 620)
    _window_ref.show()

    def _cleanup():
        try:
            _window_ref.worker.stop_server()
        except Exception:
            pass
        try:
            _window_ref.thread.quit()
            _window_ref.thread.wait(5000)
        except Exception:
            pass

    app.aboutToQuit.connect(_cleanup)

    sys.exit(app.exec())
