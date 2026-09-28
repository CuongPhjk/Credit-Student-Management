"""A short notification that slides into a reserved area of the page."""

from pathlib import Path

from PyQt6.QtCore import QEasingCurve, QSize, Qt, QTimer, QVariantAnimation
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QWidget


class InlineNotice(QWidget):
    DISPLAY_MS = 2000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._progress = 0.0
        self.banner = QFrame(self)
        self.banner.setObjectName("inlineNotice")
        layout = QHBoxLayout(self.banner)
        layout.setContentsMargins(10, 6, 12, 6)
        layout.setSpacing(8)
        icon = QSvgWidget(str(
            Path(__file__).resolve().parents[1] / "resources/icons/prohibited.svg"
        ))
        icon.setFixedSize(20, 20)
        layout.addWidget(icon)
        self.message = QLabel()
        self.message.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.message)
        self.banner.setStyleSheet("""
            QFrame#inlineNotice {
                background: #fff1f2; border: 1px solid #fecdd3;
                border-radius: 6px;
            }
            QFrame#inlineNotice QLabel {
                color: #dc2626; font-size: 13px; background: transparent;
                border: none;
            }
        """)
        self.banner.hide()
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(220)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.valueChanged.connect(self._animate)
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.dismiss)

    def sizeHint(self):
        return QSize(280, 40)

    def show_message(self, text):
        self.dismiss()
        self.message.setText(text)
        self.banner.setAccessibleName(text)
        self._position_banner()
        self.banner.show()
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        self.timer.start(self.DISPLAY_MS)

    def dismiss(self):
        self.timer.stop()
        self.animation.stop()
        self.banner.hide()
        self._progress = 0.0

    def _animate(self, value):
        self._progress = float(value)
        self._position_banner()

    def _position_banner(self):
        width = min(self.width(), self.banner.sizeHint().width())
        self.banner.setGeometry(
            self.width() - round(width * self._progress), 2,
            width, self.height() - 4,
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_banner()

    def hideEvent(self, event):
        self.dismiss()
        super().hideEvent(event)
