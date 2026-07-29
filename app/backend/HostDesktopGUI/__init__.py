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

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")

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

    # 操作系统主题变化时跟随（仅在配置为“跟随系统”时生效）
    try:
        app.styleHints().colorSchemeChanged.connect(
            lambda _scheme: _window_ref.on_system_theme_changed()
        )
    except (AttributeError, RuntimeError):
        pass

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
