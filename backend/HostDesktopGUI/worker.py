import asyncio
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal, Slot


@dataclass
class ServerState:
    url: str = ""
    running: bool = False


class ServerWorker(QObject):
    """后台线程里跑 hypercorn + HostCore 的 worker"""

    log = Signal(str)
    state_changed = Signal(object)  # ServerState

    def __init__(self, version: str = "dev"):
        super().__init__()
        self.version = version
        self._loop: asyncio.AbstractEventLoop | None = None
        self._shutdown_event: asyncio.Event | None = None
        self._state = ServerState()

    @Slot()
    def start_server(self):
        # 这个 Slot 会在 QThread 中执行（由主窗口发出 start_requested 信号）
        if self._state.running:
            self.log.emit("[info] server already running.\n")
            return

        try:
            # ⚠️ 重要：所有 HostCore 相关的 import（间接会引 pyautogui 的）
            # 都放到这里延迟导入，确保 Qt 先初始化。
            from hypercorn.config import Config as HypercornConfig
            from hypercorn.asyncio import serve

            from HostCore.http_server import HttpServer
            from HostCore.infra.files.config import Config
            from HostCore.utils.pyinstaller_context import PyInstallerContext
            from HostDesktopCLI.cli_qrcode import url_to_qrcode_print
            from HostDesktopCLI.get_address import get_address
            from HostDesktopCLI.cli_logo import cli_logo

            # 完整沿用 CLI 的逻辑
            print(cli_logo(self.version))
            Config.init()
            static_folder = PyInstallerContext().frontend_resource_path()
            app = HttpServer(static_folder)
            host_ip_address = get_address()

            # ASCII 二维码打印到“终端”（即 GUI 文本框）
            url_to_qrcode_print(host_ip_address)

            hypercorn_config = HypercornConfig()
            hypercorn_config.bind = [host_ip_address]

            # 在本线程中创建/运行 asyncio loop
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._shutdown_event = asyncio.Event()

            async def shutdown_trigger():
                await self._shutdown_event.wait()

            async def runner():
                # 拼接地址，给状态栏、托盘等使用
                if ":" in host_ip_address:
                    host, port = host_ip_address.split(":", 1)
                    self._state.url = f"http://{host}:{port}"
                else:
                    self._state.url = f"http://{host_ip_address}"

                self._state.running = True
                self.state_changed.emit(self._state)

                await serve(app, hypercorn_config, shutdown_trigger=shutdown_trigger)

                self._state.running = False
                self.state_changed.emit(self._state)

            self._loop.run_until_complete(runner())

        except Exception as exc:
            # 把异常发到 GUI 终端
            self.log.emit(f"[error] {exc}\n")
            self._state.running = False
            self.state_changed.emit(self._state)

    @Slot()
    def stop_server(self):
        if not self._state.running:
            self.log.emit("[info] server not running.\n")
            return

        if self._loop and self._shutdown_event:
            self.log.emit("[info] stopping server...\n")
            # 唤醒 shutdown_trigger，优雅停服
            self._loop.call_soon_threadsafe(self._shutdown_event.set)

    def state(self) -> ServerState:
        return self._state
