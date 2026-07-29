# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

"""解析 GUI 界面偏好（语言 / 主题）的生效值：配置文件手动值 or 跟随系统。"""

from HostCore.infra.files.config import Config
from HostDesktopGUI import gui_config, i18n


def effective_language() -> str:
    """生效语言：跟随系统 -> 系统语言；否则配置文件中的手动选择（非法值回退 zh）。"""
    if Config.Gui.LANGUAGE_FOLLOW_SYSTEM:
        return i18n.system_language()
    lang = str(Config.Gui.LANGUAGE)
    return lang if lang in (i18n.LANG_ZH, i18n.LANG_EN) else i18n.LANG_ZH


def effective_theme() -> str:
    """生效主题：跟随系统 -> 系统主题；否则配置文件中的手动选择（非法值回退 light）。"""
    if Config.Gui.THEME_FOLLOW_SYSTEM:
        return gui_config.system_theme()
    theme = str(Config.Gui.THEME)
    return theme if theme in (gui_config.THEME_LIGHT, gui_config.THEME_DARK) else gui_config.THEME_LIGHT
