# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

"""GUI 面板的轻量中英双语支持。

用法：
    from HostDesktopGUI.i18n import tr
    label.setText(tr("面板", "Panel"))
语言切换后，各界面通过 retranslate() 重新设置文案。
"""

from PySide6.QtCore import QLocale

LANG_ZH = "zh"
LANG_EN = "en"

_language = LANG_ZH


def system_language() -> str:
    """跟随系统的语言：中文环境为 zh，其余为 en。"""
    return LANG_ZH if QLocale.system().name().lower().startswith("zh") else LANG_EN


def set_language(lang: str):
    global _language
    _language = lang if lang in (LANG_ZH, LANG_EN) else LANG_ZH


def language() -> str:
    return _language


def tr(zh: str, en: str) -> str:
    """按当前语言返回文案。"""
    return zh if _language == LANG_ZH else en
