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

"""主窗口：顶部导航切换“面板 / 设置”两个界面，系统托盘，stdout 重定向到日志组件。"""

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QStackedWidget,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from HostCore.infra.files.config import Config
from HostDesktopGUI import gui_config, i18n
from HostDesktopGUI.gui_config import APP_ICON_PATH, APP_NAME
from HostDesktopGUI.gui_prefs import effective_language, effective_theme
from HostDesktopGUI.i18n import tr
from HostDesktopGUI.main_page import MainPage
from HostDesktopGUI.settings_page import SettingsPage
from HostDesktopGUI.widgets import ZoomView
from HostDesktopGUI.worker import ServerState, ServerWorker

from HostCore.utils.check_platform import is_mac


class EmittingStream(QObject):
    """把 stdout/stderr 的文本导入到主界面的日志组件。"""

    text = Signal(str)

    def write(self, s: str):
        if s:
            self.text.emit(s)

    def flush(self):
        pass

    def isatty(self) -> bool:
        return False


class MainWindow(QWidget):
    """后端面板主窗口。"""

    def __init__(self, version: str = "dev"):
        super().__init__()
        self.setObjectName("appRoot")

        # 标题 & 图标
        title = f"{APP_NAME} ({version})" if version else APP_NAME
        self.setWindowTitle(title)

        if APP_ICON_PATH.is_file():
            icon = QIcon(str(APP_ICON_PATH))
            self.setWindowIcon(icon)
        else:
            icon = self.windowIcon()

        self._really_quit = False  # 区分“关闭到托盘”和“真正退出”
        self._last_state = ServerState()  # 最近一次服务状态（托盘提示文案用）

        # 加载配置文件（供主/设置界面预填）
        Config.init()

        # --- 两个可切换的界面（设置页懒加载，加快首屏显示） ---
        self.main_page = MainPage()
        self._settings_page = None

        self.stack = QStackedWidget()
        self.stack.addWidget(self.main_page)

        # --- 顶部导航 ---
        self.nav_main = QPushButton(tr("面板", "Panel"))
        self.nav_main.setObjectName("navButton")
        self.nav_main.setCheckable(True)
        self.nav_settings = QPushButton(tr("设置", "Settings"))
        self.nav_settings.setObjectName("navButton")
        self.nav_settings.setCheckable(True)

        nav_group = QButtonGroup(self)
        nav_group.setExclusive(True)
        nav_group.addButton(self.nav_main, 0)
        nav_group.addButton(self.nav_settings, 1)
        nav_group.idToggled.connect(self._on_nav_toggled)
        self.nav_main.setChecked(True)

        nav_bar = QWidget()
        nav_bar.setObjectName("navBar")
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(4, 4, 4, 4)
        nav_layout.setSpacing(4)
        nav_layout.addWidget(self.nav_main)
        nav_layout.addWidget(self.nav_settings)

        top_row = QHBoxLayout()
        top_row.addStretch(1)
        top_row.addWidget(nav_bar)
        top_row.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(top_row, 0)
        # 窗口小于基准尺寸时，页面区域整体等比缩放
        self.zoom = ZoomView(self.stack)
        layout.addWidget(self.zoom, 1)

        # --- 后台 worker + 线程 ---
        self.worker = ServerWorker(version=version)
        self.thread = QThread(self)
        self.worker.moveToThread(self.thread)

        self.worker.log.connect(self.main_page.append_log)
        self.worker.state_changed.connect(self.main_page.on_state_changed)
        self.worker.state_changed.connect(self.on_state_changed)
        # 启动：排队到 worker 线程执行；停止：worker 线程阻塞于 asyncio loop，
        # 必须由 GUI 线程直接调用（内部 call_soon_threadsafe，线程安全）
        self.main_page.start_requested.connect(self.worker.start_server)
        self.main_page.stop_requested.connect(self._on_stop_requested)

        self.thread.start()

        # 启动横幅改到 worker 线程后台打印（重导入不阻塞首屏）
        QTimer.singleShot(0, self.worker.print_banner)

        # --- stdout/stderr -> 日志组件 ---
        self._stdout = EmittingStream()
        self._stderr = EmittingStream()
        self._stdout.text.connect(self.main_page.append_log)
        self._stderr.text.connect(self.main_page.append_log)

        import sys as _sys

        _sys.stdout = self._stdout
        _sys.stderr = self._stderr

        # --- 系统托盘图标 ---
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip(APP_NAME)
        if is_mac():
            mask_icon = QIcon(str(APP_ICON_PATH))
            mask_icon.setIsMask(True)
            self.tray_icon.setIcon(mask_icon)
        else:
            self.tray_icon.setIcon(icon)

        tray_menu = QMenu(self)
        self.action_show = tray_menu.addAction(tr("显示主窗口", "Show"))
        self.action_quit = tray_menu.addAction(tr("退出程序", "Quit"))

        self.action_show.triggered.connect(self.show_from_tray)
        self.action_quit.triggered.connect(self.quit_from_tray)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    # ---------- 界面切换（设置页懒加载） ----------

    @property
    def settings_page(self) -> SettingsPage:
        """首次访问时才构建设置页（含信号连接）。"""
        if self._settings_page is None:
            self._settings_page = SettingsPage()
            # 设置保存后：刷新主界面默认启动参数 + 实时应用语言/主题
            self._settings_page.saved.connect(self.main_page.reload_from_config)
            self._settings_page.saved.connect(self.apply_gui_prefs)
            self.stack.addWidget(self._settings_page)
        return self._settings_page

    @Slot(int, bool)
    def _on_nav_toggled(self, index: int, checked: bool):
        if not checked:
            return
        if index == 1:
            self.settings_page  # 触发懒加载
        self.stack.setCurrentIndex(index)

    # ---------- 语言 / 主题 ----------

    @Slot()
    def apply_gui_prefs(self):
        """按当前 Config 实时应用语言与主题（设置保存后调用）。"""
        lang = effective_language()
        if lang != i18n.language():
            i18n.set_language(lang)
            self.retranslate()

        theme = effective_theme()
        if theme != gui_config.theme():
            self._apply_theme(theme)

    @Slot()
    def on_system_theme_changed(self):
        """操作系统主题变化时，仅在“跟随系统”模式下跟随。"""
        if Config.Gui.THEME_FOLLOW_SYSTEM:
            theme = effective_theme()
            if theme != gui_config.theme():
                self._apply_theme(theme)

    def _apply_theme(self, theme: str):
        from PySide6.QtWidgets import QApplication

        gui_config.set_theme(theme)
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(gui_config.build_stylesheet())
        self.main_page.apply_theme()

    def retranslate(self):
        """语言切换后重设本窗口及各界面文案。"""
        self.nav_main.setText(tr("面板", "Panel"))
        self.nav_settings.setText(tr("设置", "Settings"))
        self.action_show.setText(tr("显示主窗口", "Show"))
        self.action_quit.setText(tr("退出程序", "Quit"))
        self._update_tray_tooltip()
        self.main_page.retranslate()
        if self._settings_page is not None:
            self._settings_page.retranslate()

    def _update_tray_tooltip(self):
        if self._last_state.running:
            self.tray_icon.setToolTip(f"{APP_NAME} — {tr('运行中', 'Running')} {self._last_state.url}")
        else:
            self.tray_icon.setToolTip(APP_NAME)

    # ---------- 服务控制 ----------

    @Slot()
    def _on_stop_requested(self):
        self.worker.stop_server()

    @Slot(object)
    def on_state_changed(self, st: ServerState):
        self._last_state = st
        self._update_tray_tooltip()

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
                tr("已最小化到托盘，右键托盘图标可退出。",
                   "App minimized to tray. Right-click the tray icon to quit."),
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
