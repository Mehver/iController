# BSD 3-Clause License
#
# Copyright (c) 2024 Mehver (https://github.com/Mehver). All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import asyncio
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal, Slot


@dataclass
class ServerState:
    url: str = ""
    bind: str = ""
    running: bool = False


class ServerWorker(QObject):
    """后台 QThread 中运行 hypercorn + HostCore 的 worker。

    - 启动：GUI 通过信号触发 start_server(host, port)（在 worker 线程内执行并阻塞于 asyncio loop）。
    - 停止：GUI 线程直接调用 stop_server()，内部使用 call_soon_threadsafe，线程安全。
    """

    log = Signal(str)
    state_changed = Signal(object)  # ServerState

    def __init__(self, version: str = "dev"):
        super().__init__()
        self.version = version
        self._loop: asyncio.AbstractEventLoop | None = None
        self._shutdown_event: asyncio.Event | None = None
        self._state = ServerState()

    @Slot()
    def print_banner(self):
        """在 worker 线程中打印启动横幅。

        HostDesktopCLI 包的 __init__ 会引入整个服务栈（quart/hypercorn/pyautogui），
        放到后台线程导入：既不拖慢主窗口显示，又能为首次启动服务预热模块缓存。
        """
        try:
            from HostDesktopCLI.cli_logo import cli_logo

            print(cli_logo(self.version))
        except Exception as exc:
            self.log.emit(f"[warn] failed to print banner: {exc}\n")

    @Slot(str, int)
    def start_server(self, host: str, port: int):
        """在 worker 线程中启动 Web 服务（由主界面 start_requested 信号触发）。"""
        if self._state.running:
            self.log.emit("[info] server already running.\n")
            return

        bind = f"{host}:{port}"
        try:
            # ⚠️ 重要：所有 HostCore 相关的 import（间接会引 pyautogui 的）
            # 都放到这里延迟导入，确保 Qt 先初始化。
            from hypercorn.config import Config as HypercornConfig
            from hypercorn.asyncio import serve

            from HostCore.http_server import HttpServer
            from HostCore.infra.files.config import Config
            from HostCore.utils.pyinstaller_context import PyInstallerContext

            Config.init()
            static_folder = PyInstallerContext().frontend_resource_path()
            app = HttpServer(static_folder)

            hypercorn_config = HypercornConfig()
            hypercorn_config.bind = [bind]

            # 在本线程中创建/运行 asyncio loop
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._shutdown_event = asyncio.Event()

            async def shutdown_trigger():
                await self._shutdown_event.wait()

            async def runner():
                self._state.bind = bind
                self._state.url = f"http://{bind}"
                self._state.running = True
                self.log.emit(f"[ok] web server is starting on [{bind}] ...\n")
                self.state_changed.emit(self._state)

                await serve(app, hypercorn_config, shutdown_trigger=shutdown_trigger)

                self._state.running = False
                self._state.bind = ""
                self.log.emit("[ok] server stopped.\n")
                self.state_changed.emit(self._state)

            self._loop.run_until_complete(runner())

        except Exception as exc:
            # 把异常发到 GUI 日志
            self.log.emit(f"[error] failed to start server on [{bind}]: {exc}\n")
            self._state.running = False
            self._state.bind = ""
            self.state_changed.emit(self._state)
        finally:
            if self._loop is not None:
                try:
                    self._loop.close()
                except Exception:
                    pass
                self._loop = None
                self._shutdown_event = None

    def stop_server(self):
        """停止服务。由 GUI 线程直接调用（worker 线程正阻塞在 asyncio loop 中）。"""
        if not self._state.running:
            self.log.emit("[info] server not running.\n")
            return

        if self._loop and self._shutdown_event:
            self.log.emit("[info] stopping server...\n")
            try:
                # 唤醒 shutdown_trigger，优雅停服
                self._loop.call_soon_threadsafe(self._shutdown_event.set)
            except RuntimeError:
                # loop 已关闭（服务刚好自行退出）
                pass

    def state(self) -> ServerState:
        return self._state
