# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path

# 应用名称和版本（标题栏会用到）
APP_NAME = "iController"

# 当前目录
BASE_DIR = Path(__file__).resolve().parent

# 应用图标（ico / png 均可，Windows 上推荐 ico）
ASSETS_DIR = BASE_DIR / "assets"
APP_ICON_PATH = ASSETS_DIR / "256a.ico"

# 控件小图标（QSS image: url() 使用，绝对路径在打包/开发环境均可解析）
ARROW_DOWN_LIGHT = (ASSETS_DIR / "arrow-down-light.png").as_posix()
ARROW_DOWN_DARK = (ASSETS_DIR / "arrow-down-dark.png").as_posix()
CHECK_WHITE = (ASSETS_DIR / "check-white.png").as_posix()

THEME_LIGHT = "light"
THEME_DARK = "dark"

_theme = THEME_LIGHT


def set_theme(theme: str):
    global _theme
    _theme = theme if theme in (THEME_LIGHT, THEME_DARK) else THEME_LIGHT


def theme() -> str:
    return _theme


def system_theme() -> str:
    """跟随系统的亮暗主题（检测失败时按亮色处理）。"""
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QGuiApplication

        scheme = QGuiApplication.styleHints().colorScheme()
        return THEME_DARK if scheme == Qt.ColorScheme.Dark else THEME_LIGHT
    except Exception:
        return THEME_LIGHT


_PALETTES = {
    THEME_LIGHT: {
        "window": "#f3f4f6",
        "card": "#ffffff",
        "border": "#e5e7eb",
        "text": "#1f2937",
        "text_secondary": "#6b7280",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "accent_pressed": "#1e40af",
        "accent_disabled": "#93c5fd",
        "accent_soft": "#eff6ff",
        "running": "#16a34a",
        "warning": "#d97706",
        "error": "#dc2626",
        "error_bg": "#fef2f2",
        "input_bg": "#ffffff",
        "input_bg_disabled": "#f3f4f6",
        "input_border": "#d1d5db",
        "nav_bg": "#e5e7eb",
        "nav_hover": "rgba(255, 255, 255, 0.55)",
        "nav_checked": "#ffffff",
        "menu_hover": "#eff6ff",
        "power_off_bg": "#e5e7eb",
        "power_off_fg": "#4b5563",
        "power_disabled_bg": "#d1d5db",
        "power_disabled_fg": "#9ca3af",
        "placeholder_border": "#d1d5db",
        "placeholder_fg": "#9ca3af",
        "arrow": ARROW_DOWN_LIGHT,
    },
    THEME_DARK: {
        "window": "#0f172a",
        "card": "#1e293b",
        "border": "#334155",
        "text": "#e5e7eb",
        "text_secondary": "#94a3b8",
        "accent": "#3b82f6",
        "accent_hover": "#2563eb",
        "accent_pressed": "#1d4ed8",
        "accent_disabled": "#1e3a5f",
        "accent_soft": "#2d4a72",
        "running": "#22c55e",
        "warning": "#f59e0b",
        "error": "#f87171",
        "error_bg": "#451a1a",
        "input_bg": "#0f172a",
        "input_bg_disabled": "#1e293b",
        "input_border": "#475569",
        "nav_bg": "#1e293b",
        "nav_hover": "rgba(15, 23, 42, 0.6)",
        "nav_checked": "#0f172a",
        "menu_hover": "#2d4a72",
        "power_off_bg": "#334155",
        "power_off_fg": "#cbd5e1",
        "power_disabled_bg": "#253047",
        "power_disabled_fg": "#64748b",
        "placeholder_border": "#475569",
        "placeholder_fg": "#64748b",
        "arrow": ARROW_DOWN_DARK,
    },
}


def palette() -> dict:
    """当前主题的调色板（自绘组件直接读取）。"""
    return _PALETTES[_theme]


def build_stylesheet() -> str:
    """按当前主题生成全局样式表（配合 Fusion 风格使用）。"""
    p = palette()
    return f"""
QWidget {{
    font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif;
    font-size: 13px;
    color: {p['text']};
}}
QWidget#appRoot {{
    background: {p['window']};
}}
QDialog, QMessageBox {{
    background: {p['window']};
}}

/* ---- 顶部导航 ---- */
QWidget#navBar {{
    background: {p['nav_bg']};
    border-radius: 9px;
}}
QPushButton#navButton {{
    border: none;
    border-radius: 7px;
    padding: 7px 30px;
    font-size: 14px;
    color: {p['text_secondary']};
    background: transparent;
}}
QPushButton#navButton:hover {{
    background: {p['nav_hover']};
}}
QPushButton#navButton:checked {{
    background: {p['nav_checked']};
    color: {p['accent']};
    font-weight: 600;
}}

/* ---- 卡片式分组 ---- */
QGroupBox {{
    background: {p['card']};
    border: 1px solid {p['border']};
    border-radius: 10px;
    margin-top: 14px;
    padding-top: 8px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 4px;
    color: {p['text']};
}}

/* ---- 输入控件 ---- */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit {{
    background: {p['input_bg']};
    border: 1px solid {p['input_border']};
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: {p['accent_soft']};
    selection-color: {p['text']};
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QComboBox:focus, QPlainTextEdit:focus {{
    border: 1px solid {p['accent']};
}}
QLineEdit[invalid="true"], QPlainTextEdit[invalid="true"] {{
    border: 1px solid {p['error']};
    background: {p['error_bg']};
}}
QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled {{
    background: {p['input_bg_disabled']};
    color: {p['placeholder_fg']};
}}

/* 数字输入框：隐藏无意义的上下按钮（键盘/滚轮仍可调节） */
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    width: 0px;
    border: none;
}}

/* 下拉框：补下拉展开提示箭头 */
QComboBox::drop-down {{
    border: none;
    width: 26px;
}}
QComboBox::down-arrow {{
    image: url({p['arrow']});
    width: 12px;
    height: 12px;
}}
QComboBox QAbstractItemView {{
    background: {p['card']};
    color: {p['text']};
    border: 1px solid {p['border']};
    selection-background-color: {p['accent_soft']};
    selection-color: {p['text']};
    outline: none;
}}

/* 勾选框：选中为强调色底 + 白色勾选符号，保证两种主题下的对比度 */
QCheckBox {{
    spacing: 8px;
    font-weight: 400;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {p['input_border']};
    border-radius: 4px;
    background: {p['input_bg']};
}}
QCheckBox::indicator:hover {{
    border-color: {p['accent']};
}}
QCheckBox::indicator:checked {{
    background: {p['accent']};
    border-color: {p['accent']};
    image: url({CHECK_WHITE});
}}
QCheckBox::indicator:disabled {{
    background: {p['input_bg_disabled']};
}}

/* ---- 按钮 ---- */
QPushButton {{
    background: {p['card']};
    color: {p['text']};
    border: 1px solid {p['input_border']};
    border-radius: 6px;
    padding: 6px 16px;
}}
QPushButton:hover {{
    background: {p['accent_soft']};
}}
QPushButton#primaryButton {{
    background: {p['accent']};
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 9px 24px;
    font-weight: 600;
}}
QPushButton#primaryButton:hover {{ background: {p['accent_hover']}; }}
QPushButton#primaryButton:pressed {{ background: {p['accent_pressed']}; }}
QPushButton#primaryButton:disabled {{ background: {p['accent_disabled']}; }}

QPushButton#secondaryButton {{
    background: {p['card']};
    color: {p['text']};
    border: 1px solid {p['input_border']};
    border-radius: 8px;
    padding: 9px 24px;
}}
QPushButton#secondaryButton:hover {{ background: {p['accent_soft']}; }}

/* ---- 文本标签 ---- */
QLabel#hintLabel {{ color: {p['text_secondary']}; font-weight: 400; }}
QLabel#warningLabel {{ color: {p['warning']}; font-weight: 400; }}
QLabel#errorLabel {{ color: {p['error']}; font-weight: 400; }}
QLabel#statusLabel {{ font-size: 15px; font-weight: 600; color: {p['text_secondary']}; }}
QLabel#statusLabel[running="true"] {{ color: {p['running']}; }}
QLabel#urlLabel {{ color: {p['accent']}; font-weight: 400; }}

/* ---- 菜单（含托盘右键菜单）：文字与背景保持对比色 ---- */
QMenu {{
    background: {p['card']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 8px;
    padding: 6px;
}}
QMenu::item {{
    padding: 7px 28px 7px 20px;
    border-radius: 5px;
    background: transparent;
    color: {p['text']};
}}
QMenu::item:selected {{
    background: {p['menu_hover']};
    color: {p['text']};
}}
QMenu::item:disabled {{
    color: {p['placeholder_fg']};
}}

/* ---- 滚动区域 / 滚动条 ---- */
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {p['input_border']};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {p['text_secondary']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: {p['input_border']};
    border-radius: 5px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {p['text_secondary']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}

QToolTip {{
    background: {p['card']};
    color: {p['text']};
    border: 1px solid {p['border']};
    padding: 4px 6px;
}}
"""
