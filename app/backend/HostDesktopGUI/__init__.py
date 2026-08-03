# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

import sys

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from HostCore.infra.files.config import Config
from HostDesktopGUI import gui_config, i18n
from HostDesktopGUI.gui_config import APP_NAME, APP_ICON_PATH
from HostDesktopGUI.gui_prefs import effective_language, effective_theme
from HostDesktopGUI.i18n import tr

# 单实例：锁文件与 IPC，在创建 QApplication 之前检查
from HostDesktopGUI.single_instance import (
    InstanceServer,
    attempt_primary,
    notify_primary_and_exit,
)

# 保持一个全局引用，防止窗口被 GC
_window_ref = None


def create_splash(version: str = "") -> QSplashScreen:
    """启动浮窗：图标 + 应用名，主题配色，可显示加载进度文本。"""
    p = gui_config.palette()
    width, height = 400, 250
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor(p["card"]))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(QColor(p["border"]))
    painter.drawRect(0, 0, width - 1, height - 1)

    if APP_ICON_PATH.is_file():
        icon = QIcon(str(APP_ICON_PATH)).pixmap(88, 88)
        painter.drawPixmap((width - 88) // 2, 40, icon)

    painter.setPen(QColor(p["text"]))
    font = QFont()
    font.setPointSize(14)
    font.setBold(True)
    painter.setFont(font)
    title = APP_NAME if not version else f"{APP_NAME} ({version})"
    painter.drawText(QRect(0, 140, width, 32), Qt.AlignCenter, title)
    painter.end()

    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splash.setFont(QFont("", 10))
    return splash


def _splash_message(splash: QSplashScreen, zh: str, en: str):
    splash.showMessage(
        tr(zh, en),
        Qt.AlignHCenter | Qt.AlignBottom,
        QColor(gui_config.palette()["text_secondary"]),
    )


def HostDesktopGUI(version: str = "dev"):
    """
    GUI 入口：在 iController 里用户选择 2 时调用：
        from HostDesktopGUI import HostDesktopGUI
        HostDesktopGUI("dev")
    """

    # ── 单实例检查（在 QApplication 之前，避免二实例显示任何窗口）──
    # _lock 必须保持存活以持有操作系统级文件锁，直到进程退出时自动释放。
    # 不要删除此变量，即使静态检查工具可能提示"未使用"。
    # 如果 attempt_primary 返回了 None（权限/未知错误容错），_lock 为 None 无害。
    is_primary, _lock = attempt_primary()
    if not is_primary:
        notify_primary_and_exit()
        # notify_primary_and_exit 内部调用 sys.exit(0)，不会执行到此处
        return

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")

    # 创建 IPC 服务器（首实例监听）。
    # 在 listen() 之前先连接一个缓冲处理器：_window_ref 尚未创建，
    # 若此时收到二实例的激活请求，先记下 pending 标记，等窗口就绪后回放。
    #
    # 如果 listen() 失败（极端罕见：socket 路径过长、权限异常等），
    # 释放锁并降级为"无单实例模式"继续运行 —— 当前 GUI 可用，
    # 但二实例将作为新的首实例启动，不会静默退出。
    _instance_server = InstanceServer(app)
    _pending_activation = [False]  # 用 list 装 bool，便于嵌套函数修改

    def _buffer_activation():
        _pending_activation[0] = True

    _instance_server.activate_requested.connect(_buffer_activation)
    _ipc_ok = _instance_server.listen()

    if not _ipc_ok:
        # 监听失败：断开缓冲处理器，释放锁（如持有），降级运行。
        _instance_server.activate_requested.disconnect(_buffer_activation)
        if _lock is not None:
            try:
                _lock.unlock()
            except Exception:
                pass
        import logging as _logging

        _logging.getLogger(__name__).warning(
            "IPC server failed to start — single-instance guard disabled. "
            "A second launch will start a new GUI process."
        )

    # 先加载配置，解析生效的语言/主题（首次启动默认跟随系统）
    Config.init()
    i18n.set_language(effective_language())
    gui_config.set_theme(effective_theme())

    # 启动浮窗：尽早显示，遮盖后续的模块导入与窗口构建
    splash = create_splash(version)
    splash.show()
    app.processEvents()

    try:
        _splash_message(splash, "正在加载样式…", "Loading styles…")
        app.setStyleSheet(gui_config.build_stylesheet())

        # 应用级图标（任务栏 / 对话框等）
        if APP_ICON_PATH.is_file():
            app.setWindowIcon(QIcon(str(APP_ICON_PATH)))

        _splash_message(splash, "正在加载界面模块…", "Loading UI modules…")
        app.processEvents()
        # 主窗口模块链较重，延迟到浮窗显示后再导入
        from HostDesktopGUI.main_window import MainWindow

        _splash_message(splash, "正在构建主窗口…", "Building main window…")
        app.processEvents()
        global _window_ref
        _window_ref = MainWindow(version)
        _window_ref.setMinimumSize(560, 380)
        _window_ref.resize(1100, 740)
        _window_ref.show()
    finally:
        if "_window_ref" in globals():
            splash.finish(_window_ref)
        else:
            splash.close()

    # 二实例激活 → 恢复/显示主窗口（Qt 主线程安全，信号在事件循环中触发）
    # 先断开缓冲处理器，再连接真正的恢复方法；最后回放 listen()~窗口就绪之间
    # 收到的任何激活请求（避免因信号未连接而静默丢弃）。
    # 仅在 IPC 服务器已成功监听时才执行：若 listen() 失败，_ipc_ok 为 False，
    # 此时锁已释放、缓冲区已断开，无需且不应连接 _window_ref。
    if _ipc_ok:
        _instance_server.activate_requested.disconnect(_buffer_activation)
        _instance_server.activate_requested.connect(_window_ref.show_from_tray)

        if _pending_activation[0]:
            _window_ref.show_from_tray()

    # 操作系统主题变化时跟随（仅在配置为“跟随系统”时生效）
    try:
        app.styleHints().colorSchemeChanged.connect(
            lambda _scheme: _window_ref.on_system_theme_changed()
        )
    except (AttributeError, RuntimeError):
        pass

    def _cleanup():
        try:
            _instance_server.shutdown()
        except Exception:
            pass
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
