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

"""主界面：左侧启动参数表单 + 居中大号开关 + 右侧二维码 + 下半部分终端式日志。"""

import errno
import ipaddress
import socket

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from HostCore.infra.files.config import Config
from HostDesktopGUI.i18n import tr
from HostDesktopGUI.worker import ServerState
from HostDesktopGUI.widgets import LogView, PowerButton, QRCodeView

# 绑定地址模式（对应 CLI 问卷的 4 个选项）
MODE_CONFIG = "config"
MODE_DETECTED = "detected"
MODE_BROADCAST = "broadcast"
MODE_CUSTOM = "custom"

# 布局常量
LOG_MIN = 72       # 日志区域最小高度（窗口偏矮时优先挤压日志）
POWER_MAX = 176    # 开关按钮最大直径
POWER_MIN = 92     # 开关按钮最小直径


def is_valid_ipv4(text: str) -> bool:
    """合法的 IPv4 绑定地址（排除组播地址），与 CLI 的校验规则一致。"""
    try:
        ip = ipaddress.ip_address(text.strip())
        return ip.version == 4 and not ip.is_multicast
    except ValueError:
        return False


def detect_local_ip() -> str | None:
    """检测本机局域网 IP（失败时返回 None）。"""
    try:
        from HostCore.utils.check_ip import check_ip

        return check_ip()
    except Exception:
        return None


def _errno_is(e: OSError, *names: str) -> bool:
    """跨平台 errno 比较（Windows 下 socket 错误可能是 WSA* 代码）。"""
    return any(e.errno == getattr(errno, name, None) for name in names)


def check_bind(host: str, port: int):
    """试绑定检测地址/端口可用性，返回 (是否可用, 错误类型, 提示信息)。

    错误类型："inuse"（端口被占用）/ "noaddr"（本机没有该地址）/ "other"。
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True, "", ""
        except OSError as e:
            if _errno_is(e, "EADDRINUSE", "WSAEADDRINUSE"):
                return False, "inuse", tr("端口 {port} 已被占用", "Port {port} is already in use").format(port=port)
            if _errno_is(e, "EADDRNOTAVAIL", "WSAEADDRNOTAVAIL"):
                return False, "noaddr", tr("本机没有该 IP 地址", "This IP does not exist on this machine")
            return False, "other", str(e)


class _TopRow(QWidget):
    """上半部分容器：手动布置左/中/右三个正方形区域（间隙均分，中间区域精确居中）。

    不使用 QLayout + setFixedWidth 的组合：固定尺寸会写入最小尺寸并“滞留”，
    导致窗口/缩放容器无法再把内容缩小。手动 setGeometry 不受尺寸提示影响。
    """

    def __init__(self, left: QWidget, center: QWidget, right: QWidget, parent=None):
        super().__init__(parent)
        self.left = left
        self.center = center
        self.right = right
        for w in (left, center, right):
            w.setParent(self)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def resizeEvent(self, event):
        side = self.height()
        total = 3 * side
        gap = max(0, (self.width() - total) // 4)
        x = gap
        for w in (self.left, self.center, self.right):
            w.setGeometry(x, 0, side, side)
            x += side + gap
        super().resizeEvent(event)


class MainPage(QWidget):
    """主面板页：启动参数表单（可随时修改、实时校验）+ 开关 + 二维码 + 日志。"""

    start_requested = Signal(str, int)  # host, port
    stop_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pageRoot")
        self.setAttribute(Qt.WA_StyledBackground, True)  # 普通 QWidget 需此属性才绘制样式表背景
        self._state = ServerState()
        self._busy = False  # 启动/停止过渡状态
        self._busy_kind = ""  # "starting" / "stopping"
        self._local_ip = detect_local_ip()
        self._tr_widgets = []  # (setter, zh, en) 注册表，供 retranslate 使用

        self._build_ui()
        self.reload_from_config()
        self._validate_all()

    # ---------------------------------------------------------- 文案注册

    def _tr_reg(self, setter, zh: str, en: str):
        """注册一条可翻译文案并立即生效。"""
        self._tr_widgets.append((setter, zh, en))
        setter(tr(zh, en))

    def retranslate(self):
        """语言切换后重设所有文案。"""
        for setter, zh, en in self._tr_widgets:
            setter(tr(zh, en))
        self._refresh_host_mode_texts()
        # 状态相关文案
        if self._busy:
            self.status_label.setText(self._busy_text())
        else:
            self.status_label.setText(
                tr("运行中", "Running") if self._state.running else tr("已停止", "Stopped")
            )
        self._validate_all()  # 重新生成内联提示
        self.qr_view.apply_theme()  # 占位提示文案

    def apply_theme(self):
        """主题切换后刷新自绘/独立配色组件。"""
        self.power_button.update()
        self.qr_view.apply_theme()
        self.log_view.apply_theme()

    def _busy_text(self) -> str:
        if self._busy_kind == "stopping":
            return tr("停止中…", "Stopping…")
        return tr("启动中…", "Starting…")

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 16)
        root.setSpacing(12)
        self._root_layout = root

        # ---- 上半部分：参数(左) | 开关(中) | 二维码(右)，均为尽量正方形的区域 ----
        # 左列：绑定地址 + 端口（纵向叠放）
        self.left_panel = QWidget()
        left = QVBoxLayout(self.left_panel)
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(12)

        self.bind_group = QGroupBox()
        self._tr_reg(self.bind_group.setTitle, "绑定地址", "Bind Address")
        bind_form = QFormLayout(self.bind_group)
        bind_form.setContentsMargins(12, 24, 12, 12)
        bind_form.setSpacing(10)

        self.host_mode = QComboBox()
        # 尺寸下限：布局被压缩时保证输入框与标签文字始终可见（更小窗口走整体缩放）
        self.host_mode.setMinimumWidth(120)
        self.host_mode.addItem("", MODE_CONFIG)
        self.host_mode.addItem("", MODE_DETECTED)
        self.host_mode.addItem("", MODE_BROADCAST)
        self.host_mode.addItem("", MODE_CUSTOM)
        self.host_mode.currentIndexChanged.connect(self._on_host_mode_changed)
        self.host_mode_label = QLabel()
        self.host_mode_label.setMinimumWidth(64)
        self._tr_reg(self.host_mode_label.setText, "地址来源", "Source")
        bind_form.addRow(self.host_mode_label, self.host_mode)

        self.custom_ip_label = QLabel()
        self.custom_ip_label.setMinimumWidth(64)
        self._tr_reg(self.custom_ip_label.setText, "自定义 IP", "Custom IP")
        self.custom_ip = QLineEdit()
        self.custom_ip.setMinimumWidth(108)
        self._tr_reg(self.custom_ip.setPlaceholderText, "例如 192.168.1.50", "e.g. 192.168.1.50")
        self.custom_ip.textChanged.connect(self._validate_all)
        bind_form.addRow(self.custom_ip_label, self.custom_ip)

        self.bind_hint = QLabel("")
        self.bind_hint.setObjectName("hintLabel")
        self.bind_hint.setWordWrap(True)
        bind_form.addRow(self.bind_hint)

        left.addWidget(self.bind_group, 3)

        self.port_group = QGroupBox()
        self._tr_reg(self.port_group.setTitle, "端口", "Port")
        port_form = QFormLayout(self.port_group)
        port_form.setContentsMargins(12, 24, 12, 12)
        port_form.setSpacing(10)

        self.port_spin = QSpinBox()
        self.port_spin.setMinimumWidth(92)
        self.port_spin.setRange(1, 65534)
        self.port_spin.valueChanged.connect(self._validate_all)
        self.port_label = QLabel()
        self.port_label.setMinimumWidth(64)
        self._tr_reg(self.port_label.setText, "监听端口", "Listen port")
        port_form.addRow(self.port_label, self.port_spin)

        self.port_hint = QLabel("")
        self.port_hint.setObjectName("hintLabel")
        self.port_hint.setWordWrap(True)
        port_form.addRow(self.port_hint)

        left.addWidget(self.port_group, 2)

        # 中：大号开关按钮 + 状态（固定水平居中）
        self.center_panel = QWidget()
        center_layout = QVBoxLayout(self.center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(6)
        center_layout.addStretch(1)

        self.power_button = PowerButton(POWER_MAX)
        self.power_button.clicked.connect(self._on_power_clicked)
        center_layout.addWidget(self.power_button, 0, Qt.AlignCenter)

        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setProperty("running", False)
        center_layout.addWidget(self.status_label)
        self.status_label.setText(tr("已停止", "Stopped"))

        self.dirty_label = QLabel()
        self._tr_reg(self.dirty_label.setText, "参数已修改，重启后生效", "Params changed, restart to apply")
        self.dirty_label.setObjectName("warningLabel")
        self.dirty_label.setAlignment(Qt.AlignCenter)
        self.dirty_label.hide()
        center_layout.addWidget(self.dirty_label)

        center_layout.addStretch(1)

        # 右：二维码
        self.qr_group = QGroupBox()
        self._tr_reg(self.qr_group.setTitle, "快速链接", "Quick Link")
        qr_layout = QVBoxLayout(self.qr_group)
        qr_layout.setContentsMargins(12, 24, 12, 12)
        qr_layout.setSpacing(8)

        self.qr_view = QRCodeView()
        qr_layout.addWidget(self.qr_view, 1)

        self.qr_url_label = QLabel("")
        self.qr_url_label.setObjectName("hintLabel")
        self.qr_url_label.setAlignment(Qt.AlignCenter)
        self.qr_url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        qr_layout.addWidget(self.qr_url_label)

        # 上半行：手动布置三个正方形区域（详见 _TopRow）
        self._top = _TopRow(self.left_panel, self.center_panel, self.qr_group)
        root.addWidget(self._top, 1)

        # ---- 下半部分：日志（独占，窗口偏矮时优先被压缩） ----
        self.log_group = QGroupBox()
        self._tr_reg(self.log_group.setTitle, "运行日志", "Logs")
        self.log_group.setMinimumHeight(LOG_MIN)
        log_layout = QVBoxLayout(self.log_group)
        log_layout.setContentsMargins(12, 24, 12, 12)
        self.log_view = LogView()
        log_layout.addWidget(self.log_view)

        root.addWidget(self.log_group, 1)

    # ------------------------------------------------------------ 自适应布局

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._relayout_top()

    def _relayout_top(self):
        """让上半部分的三个区域尽量为正方形；高度不足时优先压缩日志。

        - 理想：上半高度 = 可用宽度 / 3，三个区域均为正方形（_TopRow 手动布置）；
        - 窗口偏矮：日志被压到 LOG_MIN 后，上半部分再相应变矮（区域仍保持正方形）；
        - 上下高度分配用 stretch 比例实现，不写固定尺寸，避免最小尺寸滞留。
        """
        m = self._root_layout.contentsMargins()
        sp = self._root_layout.spacing()
        avail_w = self.width() - m.left() - m.right()
        avail_h = self.height() - m.top() - m.bottom() - sp
        if avail_w < 80 or avail_h < 80:
            return

        cell = (avail_w - 6 * sp) / 3.0  # 三个正方形 + 四段间隙（近似按 spacing 计）
        top_h = int(min(cell, avail_h - LOG_MIN))
        top_h = max(96, top_h)  # 极限保护

        self._root_layout.setStretchFactor(self._top, top_h)
        self._root_layout.setStretchFactor(self.log_group, max(1, avail_h - top_h))
        self.power_button.set_diameter(min(POWER_MAX, max(POWER_MIN, top_h - 116)))

    # ------------------------------------------------------------ 参数与校验

    def reload_from_config(self):
        """从 Config（即 config.yaml 的当前值）预填启动参数表单。"""
        self._refresh_host_mode_texts()
        if self.host_mode.currentData() != MODE_CONFIG:
            self.host_mode.setCurrentIndex(0)
        self.port_spin.setValue(int(Config.HttpServer.PORT))
        self._validate_all()

    def _refresh_host_mode_texts(self):
        """地址来源下拉项文案（含配置文件 HOST / 本机 IP 的动态值）。"""
        host = str(Config.HttpServer.HOST)
        self.host_mode.setItemText(0, f"{tr('配置文件', 'Config file')}（{host}）")
        ip_text = f"（{self._local_ip}）" if self._local_ip else ""
        self.host_mode.setItemText(1, f"{tr('本机 IP', 'Local IP')}{ip_text}")
        self.host_mode.setItemText(2, tr("0.0.0.0（所有接口）", "0.0.0.0 (all interfaces)"))
        self.host_mode.setItemText(3, tr("自定义", "Custom"))

    def current_params(self):
        """返回 (host, port)；参数非法时返回 None。"""
        host = self._current_host()
        if host is None:
            return None
        return host, self.port_spin.value()

    def _current_host(self) -> str | None:
        mode = self.host_mode.currentData()
        if mode == MODE_CONFIG:
            host = str(Config.HttpServer.HOST).strip()
            return host if is_valid_ipv4(host) else None
        if mode == MODE_DETECTED:
            return self._local_ip
        if mode == MODE_BROADCAST:
            return "0.0.0.0"
        # MODE_CUSTOM
        text = self.custom_ip.text().strip()
        return text if is_valid_ipv4(text) else None

    def _set_invalid(self, widget, invalid: bool):
        if widget.property("invalid") != invalid:
            widget.setProperty("invalid", invalid)
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    @Slot()
    def _on_host_mode_changed(self):
        self._validate_all()

    @Slot()
    def _validate_all(self):
        """表单每次修改时做合法性验证（内联提示 + 控制启动按钮可用性）。"""
        mode = self.host_mode.currentData()
        host = self._current_host()

        # 绑定地址校验
        custom = mode == MODE_CUSTOM
        self.custom_ip_label.setVisible(custom)
        self.custom_ip.setVisible(custom)
        self._set_invalid(self.custom_ip, custom and host is None)
        if host is None:
            if custom:
                self._set_hint(self.bind_hint, tr("请输入合法的 IPv4 地址（非组播）。",
                                                "Enter a valid IPv4 address (non-multicast)."), "errorLabel")
            elif mode == MODE_DETECTED:
                self._set_hint(self.bind_hint, tr("未能检测到本机局域网 IP。",
                                                  "Failed to detect the local LAN IP."), "errorLabel")
            else:
                self._set_hint(self.bind_hint, tr("配置文件中的 HOST 不是合法的 IPv4 地址。",
                                                  "HOST in the config file is not a valid IPv4 address."), "errorLabel")
        else:
            self._set_hint(self.bind_hint, f"{tr('将绑定', 'Will bind')}：{host}", "hintLabel")

        # 端口占用检测（仅在地址有效，且不是“本服务正在占用”时）
        port = self.port_spin.value()
        self_hold = self._state.running and f"{host}:{port}" == self._state.bind
        if host is not None and not self_hold:
            ok, kind, msg = check_bind(host, port)
            if not ok:
                # 地址缺失在地址栏提示，端口占用在端口栏提示
                if kind == "noaddr":
                    self._set_hint(self.bind_hint, f"⚠ {msg}", "warningLabel")
                    self._set_hint(self.port_hint, "", "hintLabel")
                else:
                    self._set_hint(self.port_hint, f"⚠ {msg}", "warningLabel")
            else:
                self._set_hint(self.port_hint, "", "hintLabel")
        else:
            self._set_hint(self.port_hint, "", "hintLabel")

        self._update_power_enabled()
        self._check_dirty()

    @staticmethod
    def _set_hint(label: QLabel, text: str, style_name: str):
        label.setText(text)
        if label.objectName() != style_name:
            label.setObjectName(style_name)
            label.style().unpolish(label)
            label.style().polish(label)

    def _update_power_enabled(self):
        if self._busy or self._state.running:
            self.power_button.setEnabled(not self._busy)
        else:
            self.power_button.setEnabled(self.current_params() is not None)

    def _check_dirty(self):
        """服务运行中修改了启动参数时给出提示。"""
        if not self._state.running:
            self.dirty_label.hide()
            return
        params = self.current_params()
        dirty = params is not None and f"{params[0]}:{params[1]}" != self._state.bind
        self.dirty_label.setVisible(dirty)

    # ------------------------------------------------------------ 开关与状态

    @Slot()
    def _on_power_clicked(self):
        if self._busy:
            return
        if self._state.running:
            self._set_busy(True, "stopping")
            self.stop_requested.emit()
            return

        params = self.current_params()
        if params is None:
            return
        host, port = params

        # 端口占用 -> 询问是否强制使用（对应 CLI 的 force 选项）
        ok, kind, msg = check_bind(host, port)
        if not ok:
            if kind == "inuse":
                ret = QMessageBox.question(
                    self,
                    tr("端口被占用", "Port Occupied"),
                    tr("{msg}\n\n仍要强制尝试启动吗？", "{msg}\n\nTry to start anyway?").format(msg=msg),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if ret != QMessageBox.Yes:
                    return
            else:
                QMessageBox.warning(self, tr("无法启动", "Cannot Start"), f"{msg}." if not msg.endswith("。") else msg)
                return

        self._set_busy(True, "starting")
        self.start_requested.emit(host, port)

    def _set_busy(self, busy: bool, kind: str = ""):
        self._busy = busy
        self._busy_kind = kind
        if busy:
            self.status_label.setText(self._busy_text())
        self._update_power_enabled()

    @Slot(object)
    def on_state_changed(self, st: ServerState):
        self._state = st
        self._busy = False
        self._busy_kind = ""
        self.power_button.set_running(st.running)
        self.status_label.setProperty("running", st.running)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

        if st.running:
            self.status_label.setText(tr("运行中", "Running"))
            url = self._display_url(st.bind)
            self.qr_view.set_url(url)
            self.qr_url_label.setText(url)
        else:
            self.status_label.setText(tr("已停止", "Stopped"))
            self.qr_view.clear()
            self.qr_url_label.setText("")

        self._update_power_enabled()
        self._check_dirty()

    def _display_url(self, bind: str) -> str:
        """实际访问地址：绑定 0.0.0.0 时用本机局域网 IP 展示（手机扫码不可访问 0.0.0.0）。"""
        host, _, port = bind.rpartition(":")
        if host in ("", "0.0.0.0"):
            host = self._local_ip or "127.0.0.1"
        return f"http://{host}:{port}"

    # ------------------------------------------------------------ 日志

    @Slot(str)
    def append_log(self, s: str):
        self.log_view.append_text(s)
