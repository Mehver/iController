import queue

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtGui import QFont, QTextCursor, QIcon
from PySide6.QtWidgets import (
    QWidget,
    QTextEdit,
    QLineEdit,
    QVBoxLayout,
    QSystemTrayIcon,
    QMenu,
)

from HostDesktopGUI.worker import ServerWorker, ServerState
from HostDesktopGUI.gui_config import APP_NAME, APP_ICON_PATH

from HostCore.utils.check_platform import is_mac


class EmittingStream(QObject):
    """把 stdout/stderr 的文本导入到 GUI 文本框"""

    text = Signal(str)

    def write(self, s: str):
        if s:
            self.text.emit(s)

    def flush(self):
        pass


# GUI 输入框 -> CLI input() 的“stdin 队列”
_input_queue: "queue.Queue[str]" = queue.Queue()


def gui_input(prompt: str = "") -> str:
    """
    替代内置 input() 的函数：
      - prompt 打到 stdout（即 GUI 终端）；
      - 阻塞等待用户在 GUI 输入框里敲一行；
      - 返回那一行字符串。
    """
    if prompt:
        # 和内置 input 一样：不自动换行
        print(prompt, end="", flush=True)
    line = _input_queue.get()
    return line


class ShellWindow(QWidget):
    """主窗口：上方终端，下方输入框 + 托盘图标"""

    # GUI → worker 线程的控制信号
    start_requested = Signal()
    stop_requested = Signal()

    def __init__(self, version: str = "dev"):
        super().__init__()

        # 标题 & 图标
        title = f"{APP_NAME} ({version})" if version else APP_NAME
        self.setWindowTitle(title)

        if APP_ICON_PATH.is_file():
            icon = QIcon(str(APP_ICON_PATH))
            self.setWindowIcon(icon)
        else:
            icon = self.windowIcon()

        self._really_quit = False  # 区分“关闭到托盘”和“真正退出”

        # --- 终端文本框 ---
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setLineWrapMode(QTextEdit.NoWrap)
        self.terminal.setStyleSheet("background:#0b0f14; color:#d6dde6; border:0;") # Dark theme
        # self.terminal.setStyleSheet("background:#ffffff; color:#000000; border:0;")  # Light theme
        font = QFont("Courier New")
        font.setStyleHint(QFont.Monospace)
        self.terminal.setFont(font)

        # --- 输入行 ---
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type Here 输入命令后按 Enter ...")
        self.input.returnPressed.connect(self.on_command)

        layout = QVBoxLayout()
        layout.addWidget(self.terminal, 1)
        layout.addWidget(self.input, 0)
        self.setLayout(layout)

        # --- stdout/stderr -> GUI 终端 ---
        self._stdout = EmittingStream()
        self._stderr = EmittingStream()
        self._stdout.text.connect(self.append_text)
        self._stderr.text.connect(self.append_text)

        import sys as _sys

        _sys.stdout = self._stdout
        _sys.stderr = self._stderr

        # --- 后台 worker + 线程 ---
        self.worker = ServerWorker(version=version)
        self.thread = QThread(self)
        self.worker.moveToThread(self.thread)
        self.worker.log.connect(self.append_text)
        self.worker.state_changed.connect(self.on_state_changed)

        # 通过 Signal 让 worker 在自己的线程里跑
        self.start_requested.connect(self.worker.start_server)
        self.stop_requested.connect(self.worker.stop_server)

        self.thread.start()

        # --- 系统托盘图标 ---
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip(APP_NAME)
        if is_mac:
            mask_icon = QIcon(str(APP_ICON_PATH))
            mask_icon.setIsMask(True)
            self.tray_icon.setIcon(mask_icon)
        else:
            self.tray_icon.setIcon(icon)

        tray_menu = QMenu(self)
        action_show = tray_menu.addAction("Show 显示主窗口")
        action_quit = tray_menu.addAction("Quit 退出程序")

        action_show.triggered.connect(self.show_from_tray)
        action_quit.triggered.connect(self.quit_from_tray)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

        # 窗口创建后自动启动 CLI / server
        self.start_requested.emit()

    # ---------- UI 辅助 ----------

    @Slot(str)
    def append_text(self, s: str):
        """在终端末尾追加文本"""
        self.terminal.moveCursor(QTextCursor.End)
        self.terminal.insertPlainText(s)
        self.terminal.moveCursor(QTextCursor.End)

    @Slot(object)
    def on_state_changed(self, st: ServerState):
        # 你也可以选择不在这里打印状态
        if st.running:
            self.append_text(f"[ok] running at {st.url}\n")
        else:
            self.append_text("[ok] stopped.\n")

    @Slot()
    def on_command(self):
        """
        输入框回车：
        - 把这一行回显到终端；
        - 送入 _input_queue，被 gui_input() 读取 -> CLI 的 input()。
        """
        line = self.input.text()
        self.input.clear()
        if line is None:
            line = ""

        # 回显（不加 '>'，更接近真正终端效果；你也可以改成 f"> {line}\n"）
        self.append_text(line + "\n")

        # 送入“stdin 队列”
        _input_queue.put(line)

    # ---------- 托盘相关 ----------

    @Slot()
    def show_from_tray(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    @Slot()
    def quit_from_tray(self):
        # 托盘菜单选择“退出”：真正结束程序
        from PySide6.QtWidgets import QApplication as _QApp

        self._really_quit = True
        app = _QApp.instance()
        if app is not None:
            # 先关闭窗口（会触发 closeEvent 停 worker）
            self.close()
            app.quit()

    @Slot("QSystemTrayIcon.ActivationReason")
    def on_tray_activated(self, reason):
        # 左键单击托盘图标：显示/隐藏主窗口
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show_from_tray()

    # ---------- 关闭事件 ----------

    def closeEvent(self, event):
        """
        - 默认：关闭按钮 -> 隐藏到托盘，不退出程序；
        - 托盘菜单“退出”时，会把 _really_quit 置为 True -> 真正退出。
        """
        if not self._really_quit:
            # 隐藏到托盘
            event.ignore()
            self.hide()

            # 可选：给个气泡提示
            self.tray_icon.showMessage(
                APP_NAME,
                "App minimized to tray. Right-click the tray icon to quit.",
                QSystemTrayIcon.Information,
                2000,
            )
        else:
            # 真正退出：停掉 worker / 线程 / 托盘
            try:
                self.worker.stop_server()
            except Exception:
                pass

            self.thread.quit()
            self.thread.wait(5000)

            if self.tray_icon is not None:
                self.tray_icon.hide()

            event.accept()
