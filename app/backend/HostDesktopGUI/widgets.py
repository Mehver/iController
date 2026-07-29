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

"""主界面使用的通用组件：终端日志视图、二维码视图、大号电源开关按钮、等比缩放容器。"""

import io

import segno
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap, QTextCursor, QTransform
from PySide6.QtWidgets import (
    QAbstractButton,
    QFrame,
    QGraphicsScene,
    QGraphicsView,
    QLabel,
    QPlainTextEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from HostDesktopGUI.gui_config import palette
from HostDesktopGUI.i18n import tr


class LogView(QPlainTextEdit):
    """终端风格的仅输出日志组件。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setMaximumBlockCount(8000)  # 限制行数，避免无限增长

        font = QFont("Courier New")
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        self.apply_theme()

    def apply_theme(self):
        """按主题刷新配色（亮色主题白底黑字，暗色主题深灰底浅字）。"""
        p = palette()
        self.setStyleSheet(
            f"QPlainTextEdit {{"
            f"  background: {p['log_bg']}; color: {p['log_fg']}; border: none;"
            f"  border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;"
            f"  padding: 6px;"
            f"}}"
        )

    def append_text(self, s: str):
        """在终端末尾追加文本并保持滚动到底部。"""
        if not s:
            return
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(s)
        self.moveCursor(QTextCursor.End)


class QRCodeView(QWidget):
    """快速链接二维码组件。

    segno 原生支持输出 PNG（纯 Python 实现，无额外依赖），
    这是 Qt 中最简单的渲染方式：PNG 字节 -> QPixmap -> QLabel。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap()

        self._label = QLabel()
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setMinimumSize(96, 96)
        self._label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)

        self.clear()

    def set_url(self, url: str):
        """根据 URL 生成并显示二维码。"""
        try:
            buf = io.BytesIO()
            segno.make(url).save(buf, kind="png", scale=8, border=2)
            pixmap = QPixmap()
            pixmap.loadFromData(buf.getvalue())
        except Exception:
            pixmap = QPixmap()

        if pixmap.isNull():
            self.clear()
            return
        self._pixmap = pixmap
        self._render()

    def clear(self):
        """清除二维码，显示占位提示。"""
        p = palette()
        self._pixmap = QPixmap()
        self._label.setPixmap(QPixmap())
        self._label.setText(tr("服务启动后\n显示二维码", "QR code appears\nwhen running"))
        self._label.setStyleSheet(
            f"color: {p['placeholder_fg']};"
            f" border: 1px dashed {p['placeholder_border']}; border-radius: 8px;"
        )

    def apply_theme(self):
        """主题/语言切换后刷新占位样式（二维码图片本身黑白配色，无需重绘）。"""
        if self._pixmap.isNull():
            self.clear()

    def _render(self):
        if self._pixmap.isNull():
            return
        self._label.setStyleSheet("")
        self._label.setPixmap(
            self._pixmap.scaled(
                self._label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )

    def resizeEvent(self, event):
        self._render()
        super().resizeEvent(event)


class PowerButton(QAbstractButton):
    """大号圆形电源开关按钮（自绘，跨平台不依赖符号字体）。"""

    def __init__(self, diameter: int = 160, parent=None):
        super().__init__(parent)
        self._running = False
        self.setFixedSize(diameter, diameter)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)

    def set_diameter(self, diameter: int):
        """随布局空间调整按钮直径。"""
        diameter = max(64, int(diameter))
        if diameter != self.width():
            self.setFixedSize(diameter, diameter)
            self.update()

    def set_running(self, running: bool):
        if self._running != running:
            self._running = running
            self.update()

    def is_running(self) -> bool:
        return self._running

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        p = palette()

        side = min(self.width(), self.height())
        margin = side * 0.04
        rect = QRectF(margin, margin, side - 2 * margin, side - 2 * margin)

        # 背景圆
        if not self.isEnabled():
            bg = QColor(p["power_disabled_bg"])
        elif self._running:
            bg = QColor(p["running"])
        else:
            bg = QColor(p["power_off_bg"])
        if self.isEnabled():
            if self.isDown():
                bg = bg.darker(115)
            elif self.underMouse():
                bg = bg.darker(108)

        painter.setPen(Qt.NoPen)
        painter.setBrush(bg)
        painter.drawEllipse(rect)

        # 电源符号：顶部留缺口的圆弧 + 竖线
        if not self.isEnabled():
            fg = QColor(p["power_disabled_fg"])
        elif self._running:
            fg = QColor(p["running_fg"])
        else:
            fg = QColor(p["power_off_fg"])

        pen = QPen(fg)
        pen.setWidthF(side * 0.055)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        cx, cy = rect.center().x(), rect.center().y()
        radius = side * 0.26
        arc_rect = QRectF(cx - radius, cy - radius, 2 * radius, 2 * radius)
        # Qt 中 0° 在 3 点钟方向、逆时针为正；顶部（90°）留 ±40° 缺口
        painter.drawArc(arc_rect, int((90 + 40) * 16), int((360 - 80) * 16))
        painter.drawLine(
            QPointF(cx, cy - radius * 1.25), QPointF(cx, cy - radius * 0.15)
        )
        painter.end()


class ZoomView(QGraphicsView):
    """等比缩放容器：窗口小于基准尺寸时，对内容整体等比缩小（类似缩放显示）。

    内容始终按不小于基准尺寸的“逻辑尺寸”布局，不小于基准时缩放比为 1（正常显示）。
    """

    BASE_W = 760   # 基准宽（内容逻辑尺寸下限，需容纳左格“标签+输入框”的下限宽度；小于此宽度才触发等比缩放）
    BASE_H = 400   # 基准高（大于此高度的窗口先用自适应布局压缩日志）

    def __init__(self, content: QWidget, parent=None):
        super().__init__(parent)
        self._content = content
        scene = QGraphicsScene(self)
        self._proxy = scene.addWidget(content)
        self.setScene(scene)

        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent;")
        self._scale = 1.0
        # 场景背景与全局窗口色保持一致（内容缩放/尺寸过渡时露出的缝隙不串色）
        self.apply_theme()

    def apply_theme(self):
        """主题切换后同步场景背景色。"""
        self.setBackgroundBrush(QColor(palette()["window"]))

    def scale_factor(self) -> float:
        return self._scale

    def resizeEvent(self, event):
        vw = max(1, self.width())
        vh = max(1, self.height())

        # 期望逻辑尺寸：不小于基准、不小于视图（视图更大时正常拉伸，无缩放）
        self._content.resize(max(self.BASE_W, vw), max(self.BASE_H, vh))
        # 内容可能被自身最小尺寸撑大，按实际尺寸计算缩放比，保证完整可见
        aw = max(1, self._content.width())
        ah = max(1, self._content.height())
        s = min(1.0, vw / aw, vh / ah)
        self._scale = s

        self._proxy.setTransform(QTransform().scale(s, s))
        self.setSceneRect(0, 0, aw * s, ah * s)
        super().resizeEvent(event)
