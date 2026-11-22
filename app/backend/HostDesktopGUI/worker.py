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
import socket
import threading
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal, Slot


@dataclass(frozen=True)
class ServerState:
    url: str = ""
    bind: str = ""
    running: bool = False
    phase: str = 'stopped'
    error: str = ''
    request_id: int = 0


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
        self._control_lock = threading.Lock()
        self._request_counter = self._pending_id = 0
        self._stop_requested = threading.Event()

    @Slot()
    def print_banner(self):
        """在 worker 线程中打印启动横幅并预热亮度、音量控制。

        此 slot 在主窗口构建后、HTTP 服务启动前执行，因此控制后端的首次导入和
        探测不会阻塞 Qt 主线程。
        """
        try:
            from HostDesktopCLI.cli_logo import cli_logo

            print(cli_logo(self.version))
        except Exception as exc:
            self.log.emit(f"[warn] failed to print banner: {exc}\n")

        try:
            from HostCore.control_warmup import warmup_controls

            warmup_controls()
        except Exception as exc:
            self.log.emit(f"[warn] control warmup skipped: {exc}\n")

    def prepare_start(self):
        """Reserve a queued start; a stop can cancel it even before its slot runs."""
        with self._control_lock:
            self._request_counter += 1
            self._pending_id = self._request_counter
            self._stop_requested = threading.Event()
            return self._pending_id

    def _publish(self, host, port, phase, request_id, error=''):
        bind = f'{host}:{port}' if phase != 'stopped' else ''
        self._state = ServerState(url=f'http://{bind}' if bind else '', bind=bind,
                                  running=phase == 'running', phase=phase,
                                  error=error, request_id=request_id)
        self.state_changed.emit(self._state)

    @staticmethod
    def _listener_addresses(host, port):
        """GUI listeners are IPv4/localhost TCP, with no ephemeral port zero."""
        if type(port) is not int or not 1 <= port <= 65534:
            raise ValueError('GUI listener port must be an integer from 1 to 65534.')
        return frozenset(info[4][0] for info in socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM))

    @staticmethod
    def _listener_matches(server, addresses, port):
        if not server.is_serving():
            return False
        for sock in server.sockets or ():
            try:
                address = sock.getsockname()
                if sock.family == socket.AF_INET and address[0] in addresses and address[1] == port:
                    return True
            except (OSError, IndexError, TypeError):
                continue
        return False

    @Slot(str, int, int)
    def start_server(self, host: str, port: int, request_id=0):
        """在 worker 线程中启动 Web 服务（由主界面 start_requested 信号触发）。"""
        if self._state.phase != 'stopped':
            self.log.emit('[info] server worker is busy or requires application restart.\n')
            return

        bind = f"{host}:{port}"
        request_id = request_id or self.prepare_start()
        with self._control_lock:
            if request_id != self._pending_id:
                return
            stop_requested = self._stop_requested
        error = ''
        reusable = True
        listeners = []
        self._publish(host, port, 'starting', request_id)
        try:
            if stop_requested.is_set():
                return
            # HTTP 服务栈相关的 import（间接会引 pyautogui）仍延迟到这里，
            # 确保 Qt 先初始化；控制后端已在 print_banner 中单独预热。
            from hypercorn.config import Config as HypercornConfig
            from hypercorn.asyncio import serve

            from HostCore.http_server import HttpServer
            from HostCore.utils.pyinstaller_context import PyInstallerContext

            static_folder = PyInstallerContext().frontend_resource_path()
            app = HttpServer(static_folder)

            hypercorn_config = HypercornConfig()
            hypercorn_config.bind = [bind]
            expected_addresses = self._listener_addresses(host, port)

            # 在本线程中创建/运行 asyncio loop
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._shutdown_event = asyncio.Event()
            if stop_requested.is_set():
                self._shutdown_event.set()

            # Hypercorn 0.16 calls asyncio.start_server only AFTER lifespan
            # startup and socket binding. Its awaited loop.create_server returns
            # an actually listening Server. Verify its resolved IPv4 address,
            # port and serve-task ownership on this private loop, not a lifespan
            # hook or speculative bind preflight.
            create_server = self._loop.create_server
            serve_owner = None
            async def listening_server(*args, **kwargs):
                server = await create_server(*args, **kwargs)
                listeners.append(server)
                owner = asyncio.current_task()
                if owner is serve_owner and not self._listener_matches(server, expected_addresses, port):
                    raise RuntimeError('Created listener does not match the expected IPv4 address/port.')
                def confirm_listener():
                    if owner is not serve_owner or owner.done() or stop_requested.is_set():
                        return
                    if self._listener_matches(server, expected_addresses, port) and not self._state.running:
                        self._publish(host, port, 'running', request_id)
                        self.log.emit(f'[ok] listener ready on [{bind}]\n')
                # Give immediate serve/startup exceptions a chance to finish the
                # owner task; this is one loop turn, not a guessed sleep/timer.
                self._loop.call_soon(confirm_listener)
                return server
            self._loop.create_server = listening_server

            async def shutdown_trigger():
                await self._shutdown_event.wait()

            async def runner():
                nonlocal serve_owner
                serve_owner = asyncio.current_task()
                self.log.emit(f"[ok] web server is starting on [{bind}] ...\n")
                await serve(app, hypercorn_config, shutdown_trigger=shutdown_trigger)

            self._loop.run_until_complete(runner())
            if not stop_requested.is_set():
                raise RuntimeError('Server exited unexpectedly.' if self._state.running else
                                   'Server exited before a listener became ready.')

        except asyncio.CancelledError:
            if not stop_requested.is_set():
                error = 'Server task was cancelled unexpectedly.'
                self.log.emit(f'[error] {error}\n')
        except Exception as exc:
            # 把异常发到 GUI 日志
            action = 'server failed' if self._state.running else 'failed to start server'
            self.log.emit(f'[error] {action} on [{bind}]: {exc}\n')
            error = str(exc) or type(exc).__name__
        finally:
            if self._loop is not None:
                try:
                    for server in listeners:
                        server.close()
                    pending = asyncio.all_tasks(self._loop)
                    for task in pending:
                        task.cancel()
                    if pending:
                        self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    for server in listeners:
                        self._loop.run_until_complete(server.wait_closed())
                    self._loop.run_until_complete(self._loop.shutdown_asyncgens())
                except Exception:
                    pass
                finally:
                    try:
                        self._loop.close()
                    except Exception as exc:
                        reusable = False
                        error = f'{error}; event loop close failed; application restart required: {exc}'
                        self.log.emit(f'[error] {error}\n')
                self._loop = None
                self._shutdown_event = None
            with self._control_lock:
                if self._pending_id == request_id:
                    self._pending_id = 0
            if reusable:
                self.log.emit('[ok] server stopped; event loop closed.\n')
            self._publish(host, port, 'stopped' if reusable else 'failed', request_id, error)

    def stop_server(self):
        """停止服务。由 GUI 线程直接调用（worker 线程正阻塞在 asyncio loop 中）。"""
        with self._control_lock:
            self._stop_requested.set()
        loop, event = self._loop, self._shutdown_event
        if loop is not None and event is not None:
            self.log.emit("[info] stopping server...\n")
            try:
                # 唤醒 shutdown_trigger，优雅停服
                loop.call_soon_threadsafe(event.set)
            except RuntimeError:
                # loop 已关闭（服务刚好自行退出）
                pass

    def state(self) -> ServerState:
        return self._state
