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

"""设置界面：以表单方式编辑外挂配置文件 config.yaml 中的所有配置（含 GUI 语言/主题）。"""

import ipaddress

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from HostCore.infra.files.config import Config
from HostDesktopGUI import gui_config, i18n
from HostDesktopGUI.i18n import tr
from HostDesktopGUI.main_page import _make_click_clear_focus, is_valid_ipv4


def parse_ip_list(text: str):
    """解析“每行一个 IP”的文本，返回 (ip 列表, 第一个非法行或 None)。"""
    ips = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ipaddress.ip_address(line)
        except ValueError:
            return ips, line
        ips.append(line)
    return ips, None


class SettingsPage(QWidget):
    """config.yaml 配置编辑页。

    保存时同时更新内存中的 Config（运行中的服务实时生效，无需重启）并写回配置文件。
    """

    saved = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pageRoot")
        self.setAttribute(Qt.WA_StyledBackground, True)  # 普通 QWidget 需此属性才绘制样式表背景
        self._tr_widgets = []  # (setter, zh, en) 注册表，供 retranslate 使用
        self._build_ui()
        self.load_from_config()

    # ---------------------------------------------------------- 文案注册

    def _tr_reg(self, setter, zh: str, en: str):
        self._tr_widgets.append((setter, zh, en))
        setter(tr(zh, en))

    def retranslate(self):
        """语言切换后重设所有文案。"""
        for setter, zh, en in self._tr_widgets:
            setter(tr(zh, en))
        self.theme_combo.setItemText(0, tr("亮色", "Light"))
        self.theme_combo.setItemText(1, tr("暗色", "Dark"))
        self.hint_label.setText("")

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 16)
        root.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setContentsMargins(0, 0, 8, 0)
        scroll_layout.setSpacing(12)

        # ---- 界面 GUI ----
        self.gui_group = QGroupBox()
        self._tr_reg(self.gui_group.setTitle, "界面", "Interface")
        gui_form = QFormLayout(self.gui_group)
        gui_form.setContentsMargins(12, 24, 12, 12)
        gui_form.setSpacing(10)

        self.lang_follow = QCheckBox()
        self._tr_reg(self.lang_follow.setText, "跟随系统", "Follow system")
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("中文", i18n.LANG_ZH)
        self.lang_combo.addItem("English", i18n.LANG_EN)
        self.lang_follow.toggled.connect(self._on_lang_follow_toggled)
        lang_row = QWidget()
        lang_layout = QHBoxLayout(lang_row)
        lang_layout.setContentsMargins(0, 0, 0, 0)
        lang_layout.addWidget(self.lang_follow)
        lang_layout.addWidget(self.lang_combo, 1)
        self.lang_label = QLabel()
        self._tr_reg(self.lang_label.setText, "LANGUAGE（语言）", "LANGUAGE (Language)")
        gui_form.addRow(self.lang_label, lang_row)

        self.theme_follow = QCheckBox()
        self._tr_reg(self.theme_follow.setText, "跟随系统", "Follow system")
        self.theme_combo = QComboBox()
        self.theme_combo.addItem(tr("亮色", "Light"), gui_config.THEME_LIGHT)
        self.theme_combo.addItem(tr("暗色", "Dark"), gui_config.THEME_DARK)
        self.theme_follow.toggled.connect(self._on_theme_follow_toggled)
        theme_row = QWidget()
        theme_layout = QHBoxLayout(theme_row)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.addWidget(self.theme_follow)
        theme_layout.addWidget(self.theme_combo, 1)
        self.theme_label = QLabel()
        self._tr_reg(self.theme_label.setText, "THEME（主题）", "THEME (Theme)")
        gui_form.addRow(self.theme_label, theme_row)

        scroll_layout.addWidget(self.gui_group)

        # ---- 控制 Control ----
        self.control_group = QGroupBox()
        self._tr_reg(self.control_group.setTitle, "控制", "Control")
        control_form = QFormLayout(self.control_group)
        control_form.setContentsMargins(12, 24, 12, 12)
        control_form.setSpacing(10)

        self.tpad_sensitivity = QDoubleSpinBox()
        self.tpad_sensitivity.setDecimals(2)
        self.tpad_sensitivity.setRange(0.05, 10.0)
        self.tpad_sensitivity.setSingleStep(0.05)
        self.tpad_label = QLabel()
        self._tr_reg(self.tpad_label.setText, "TPad_SENSITIVITY（触控板灵敏度）",
                     "TPad_SENSITIVITY (Touchpad sensitivity)")
        control_form.addRow(self.tpad_label, self.tpad_sensitivity)

        self.mwheel_sensitivity = QDoubleSpinBox()
        self.mwheel_sensitivity.setDecimals(2)
        self.mwheel_sensitivity.setRange(0.0, 100.0)
        self.mwheel_sensitivity.setSingleStep(0.5)
        self.mwheel_sens_label = QLabel()
        self._tr_reg(self.mwheel_sens_label.setText, "MWheel_SENSITIVITY（滚轮灵敏度）",
                     "MWheel_SENSITIVITY (Wheel sensitivity)")
        control_form.addRow(self.mwheel_sens_label, self.mwheel_sensitivity)

        self.mwheel_constant = QSpinBox()
        self.mwheel_constant.setRange(-9999, 9999)
        self.mwheel_const_label = QLabel()
        self._tr_reg(self.mwheel_const_label.setText, "MWheel_CONSTANT（滚轮常量）",
                     "MWheel_CONSTANT (Wheel constant)")
        control_form.addRow(self.mwheel_const_label, self.mwheel_constant)

        scroll_layout.addWidget(self.control_group)

        # ---- HTTP 服务 HttpServer ----
        self.http_group = QGroupBox()
        self._tr_reg(self.http_group.setTitle, "HTTP 服务", "HTTP Server")
        http_form = QFormLayout(self.http_group)
        http_form.setContentsMargins(12, 24, 12, 12)
        http_form.setSpacing(10)

        self.host_edit = QLineEdit()
        self._tr_reg(self.host_edit.setPlaceholderText, "例如 0.0.0.0 或 192.168.1.50",
                     "e.g. 0.0.0.0 or 192.168.1.50")
        self.host_edit.textChanged.connect(self._validate_host)
        self.host_label = QLabel()
        self._tr_reg(self.host_label.setText, "HOST（绑定地址）", "HOST (Bind address)")
        http_form.addRow(self.host_label, self.host_edit)

        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65534)
        self.port_label = QLabel()
        self._tr_reg(self.port_label.setText, "PORT（端口）", "PORT (Port)")
        http_form.addRow(self.port_label, self.port_spin)

        self.ip_mode = QComboBox()
        self.ip_mode.addItem("blacklist", "blacklist")
        self.ip_mode.addItem("whitelist", "whitelist")
        self.ip_mode_label = QLabel()
        self._tr_reg(self.ip_mode_label.setText, "IP_CHECK_MODE（IP 检查模式）",
                     "IP_CHECK_MODE (IP check mode)")
        http_form.addRow(self.ip_mode_label, self.ip_mode)

        self.blacklist_edit = self._make_ip_list_edit()
        self.blacklist_label = QLabel()
        self._tr_reg(self.blacklist_label.setText, "IP_BLACKLIST（黑名单，每行一个 IP）",
                     "IP_BLACKLIST (Blacklist, one IP per line)")
        http_form.addRow(self.blacklist_label, self.blacklist_edit)

        self.whitelist_edit = self._make_ip_list_edit()
        self.whitelist_label = QLabel()
        self._tr_reg(self.whitelist_label.setText, "IP_WHITELIST（白名单，每行一个 IP）",
                     "IP_WHITELIST (Whitelist, one IP per line)")
        http_form.addRow(self.whitelist_label, self.whitelist_edit)

        scroll_layout.addWidget(self.http_group)

        # ---- 日志 Log ----
        self.log_group = QGroupBox()
        self._tr_reg(self.log_group.setTitle, "日志", "Log")
        log_layout = QVBoxLayout(self.log_group)
        log_layout.setContentsMargins(12, 24, 12, 12)
        log_layout.setSpacing(10)

        self.log_action = QCheckBox()
        self._tr_reg(self.log_action.setText, "SERVER_ACTION_LOG — 将操作日志写入文件",
                     "SERVER_ACTION_LOG — Write action logs to file")
        self.log_ips = QCheckBox()
        self._tr_reg(self.log_ips.setText, "SERVER_IPS_LOG — 记录首次连接的 IP",
                     "SERVER_IPS_LOG — Log first-seen IPs")
        self.log_connection = QCheckBox()
        self._tr_reg(self.log_connection.setText, "SERVER_CONNECTION_LOG — 记录每次连接",
                     "SERVER_CONNECTION_LOG — Log every connection")
        self.log_keyboard = QCheckBox()
        self._tr_reg(self.log_keyboard.setText, "KEYBOARD_TEXT_LOG — 记录键盘输入文本",
                     "KEYBOARD_TEXT_LOG — Log keyboard text")
        for cb in (self.log_action, self.log_ips, self.log_connection, self.log_keyboard):
            log_layout.addWidget(cb)

        scroll_layout.addWidget(self.log_group)
        scroll_layout.addStretch(1)

        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        # 点击空白区域时释放输入控件的焦点
        _make_click_clear_focus(self)
        for c in (self.gui_group, self.control_group, self.http_group, self.log_group, container):
            _make_click_clear_focus(c)

        # ---- 底部按钮 ----
        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        self.hint_label = QLabel("")
        self.hint_label.setObjectName("hintLabel")
        buttons.addWidget(self.hint_label, 1)

        self.reload_button = QPushButton()
        self._tr_reg(self.reload_button.setText, "从文件重新加载", "Reload from File")
        self.reload_button.setObjectName("secondaryButton")
        self.reload_button.clicked.connect(self.reload_from_file)
        buttons.addWidget(self.reload_button)

        self.save_button = QPushButton()
        self._tr_reg(self.save_button.setText, "保存到配置文件", "Save to Config File")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save)
        buttons.addWidget(self.save_button)

        root.addLayout(buttons, 0)

    def _make_ip_list_edit(self) -> QPlainTextEdit:
        edit = QPlainTextEdit()
        self._tr_reg(edit.setPlaceholderText, "每行一个 IP，例如：\n192.168.1.10",
                     "One IP per line, e.g.:\n192.168.1.10")
        edit.setFixedHeight(84)
        edit.textChanged.connect(lambda e=edit: self._validate_ip_list(e))
        return edit

    # -------------------------------------------------- 语言/主题跟随系统

    @Slot(bool)
    def _on_lang_follow_toggled(self, checked: bool):
        self.lang_combo.setEnabled(not checked)
        if checked:
            self.lang_combo.setCurrentIndex(
                0 if i18n.system_language() == i18n.LANG_ZH else 1
            )

    @Slot(bool)
    def _on_theme_follow_toggled(self, checked: bool):
        self.theme_combo.setEnabled(not checked)
        if checked:
            self.theme_combo.setCurrentIndex(
                0 if gui_config.system_theme() == gui_config.THEME_LIGHT else 1
            )

    # ------------------------------------------------------------ 加载/保存

    def load_from_config(self):
        """把 Config 当前值填入表单。"""
        # GUI 偏好
        self.lang_follow.setChecked(bool(Config.Gui.LANGUAGE_FOLLOW_SYSTEM))
        self._on_lang_follow_toggled(self.lang_follow.isChecked())
        if not self.lang_follow.isChecked():
            self.lang_combo.setCurrentIndex(
                0 if str(Config.Gui.LANGUAGE) != i18n.LANG_EN else 1
            )
        self.theme_follow.setChecked(bool(Config.Gui.THEME_FOLLOW_SYSTEM))
        self._on_theme_follow_toggled(self.theme_follow.isChecked())
        if not self.theme_follow.isChecked():
            self.theme_combo.setCurrentIndex(
                0 if str(Config.Gui.THEME) != gui_config.THEME_DARK else 1
            )

        self.tpad_sensitivity.setValue(float(Config.Control.TPad_SENSITIVITY))
        self.mwheel_sensitivity.setValue(float(Config.Control.MWheel_SENSITIVITY))
        self.mwheel_constant.setValue(int(Config.Control.MWheel_CONSTANT))

        self.host_edit.setText(str(Config.HttpServer.HOST))
        self.port_spin.setValue(int(Config.HttpServer.PORT))
        index = self.ip_mode.findData(str(Config.HttpServer.IP_CHECK_MODE))
        self.ip_mode.setCurrentIndex(index if index >= 0 else 0)
        self.blacklist_edit.setPlainText("\n".join(map(str, Config.HttpServer.IP_BLACKLIST)))
        self.whitelist_edit.setPlainText("\n".join(map(str, Config.HttpServer.IP_WHITELIST)))

        self.log_action.setChecked(bool(Config.Log.SERVER_ACTION_LOG))
        self.log_ips.setChecked(bool(Config.Log.SERVER_IPS_LOG))
        self.log_connection.setChecked(bool(Config.Log.SERVER_CONNECTION_LOG))
        self.log_keyboard.setChecked(bool(Config.Log.KEYBOARD_TEXT_LOG))

        self._validate_host()
        self._validate_ip_list(self.blacklist_edit)
        self._validate_ip_list(self.whitelist_edit)

    @Slot()
    def reload_from_file(self):
        """放弃未保存的修改，从 config.yaml 重新加载。"""
        Config.init()
        self.load_from_config()
        self.hint_label.setText(tr("已从配置文件重新加载。", "Reloaded from config file."))
        print("[ok] configuration reloaded from config.yaml.")

    @Slot()
    def save(self):
        """校验并保存：更新内存 Config（运行中服务实时生效）+ 写回 config.yaml。"""
        errors = self._collect_errors()
        if errors:
            QMessageBox.warning(
                self,
                tr("配置不合法", "Invalid Configuration"),
                tr("请先修正以下问题：", "Please fix the following:") + "\n\n" + "\n".join(f"· {e}" for e in errors),
            )
            return

        # GUI 偏好（跟随系统时保留手动备选值不变）
        Config.Gui.LANGUAGE_FOLLOW_SYSTEM = self.lang_follow.isChecked()
        if not self.lang_follow.isChecked():
            Config.Gui.LANGUAGE = self.lang_combo.currentData()
        Config.Gui.THEME_FOLLOW_SYSTEM = self.theme_follow.isChecked()
        if not self.theme_follow.isChecked():
            Config.Gui.THEME = self.theme_combo.currentData()

        Config.Control.TPad_SENSITIVITY = self.tpad_sensitivity.value()
        Config.Control.MWheel_SENSITIVITY = self.mwheel_sensitivity.value()
        Config.Control.MWheel_CONSTANT = self.mwheel_constant.value()

        Config.HttpServer.HOST = self.host_edit.text().strip()
        Config.HttpServer.PORT = self.port_spin.value()
        Config.HttpServer.IP_CHECK_MODE = self.ip_mode.currentData()
        Config.HttpServer.IP_BLACKLIST, _ = parse_ip_list(self.blacklist_edit.toPlainText())
        Config.HttpServer.IP_WHITELIST, _ = parse_ip_list(self.whitelist_edit.toPlainText())

        Config.Log.SERVER_ACTION_LOG = self.log_action.isChecked()
        Config.Log.SERVER_IPS_LOG = self.log_ips.isChecked()
        Config.Log.SERVER_CONNECTION_LOG = self.log_connection.isChecked()
        Config.Log.KEYBOARD_TEXT_LOG = self.log_keyboard.isChecked()

        try:
            Config.save()
        except OSError as e:
            QMessageBox.critical(self, tr("保存失败", "Save Failed"),
                                 tr("无法写入配置文件：", "Failed to write config file:") + f"\n{e}")
            return

        self.hint_label.setText(tr("已保存到 config.yaml（运行中的服务实时生效）。",
                                   "Saved to config.yaml (applied live to the running service)."))
        print("[ok] configuration saved to config.yaml.")
        self.saved.emit()

    # ------------------------------------------------------------ 校验

    def _collect_errors(self) -> list:
        errors = []
        if not is_valid_ipv4(self.host_edit.text()):
            errors.append(tr("HOST 不是合法的 IPv4 地址", "HOST is not a valid IPv4 address"))
        for name, edit in (
            ("IP_BLACKLIST", self.blacklist_edit),
            ("IP_WHITELIST", self.whitelist_edit),
        ):
            _, bad = parse_ip_list(edit.toPlainText())
            if bad is not None:
                errors.append(
                    tr("{name} 中存在非法 IP：{bad}", "{name} contains an invalid IP: {bad}")
                    .format(name=name, bad=bad)
                )
        return errors

    @Slot()
    def _validate_host(self):
        self._set_invalid(self.host_edit, not is_valid_ipv4(self.host_edit.text()))

    @Slot()
    def _validate_ip_list(self, edit: QPlainTextEdit):
        _, bad = parse_ip_list(edit.toPlainText())
        self._set_invalid(edit, bad is not None)

    @staticmethod
    def _set_invalid(widget, invalid: bool):
        if widget.property("invalid") != invalid:
            widget.setProperty("invalid", invalid)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
