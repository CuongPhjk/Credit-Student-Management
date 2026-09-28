"""Shared campus backgrounds and PTIT identity for the application shell."""

from pathlib import Path

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget


IMAGES = Path(__file__).resolve().parents[1] / "resources" / "images"


class CampusBackground(QFrame):
    """Fill the frame with campus artwork without stretching its proportions."""

    def __init__(self, parent=None, *, header=False):
        super().__init__(parent)
        self._header = header
        filename = "background1.png" if header else "background_bar.png"
        self._background = QPixmap(str(IMAGES / filename))

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.fillRect(self.rect(), QColor("#f3f9fd" if self._header else "#123f68"))
        if not self._background.isNull() and self.width() and self.height():
            scale = max(self.width() / self._background.width(),
                        self.height() / self._background.height())
            width, height = self.width() / scale, self.height() / scale
            source = QRectF(
                (self._background.width() - width) / 2,
                (self._background.height() - height) * (.42 if self._header else .5),
                width, height,
            )
            painter.drawPixmap(QRectF(self.rect()), self._background, source)
        if self._header:
            fade = QLinearGradient(0, 0, self.width(), 0)
            fade.setColorAt(0, QColor(243, 249, 253, 250))
            fade.setColorAt(.35, QColor(243, 249, 253, 230))
            fade.setColorAt(.7, QColor(243, 249, 253, 65))
            fade.setColorAt(1, QColor(243, 249, 253, 30))
            painter.fillRect(self.rect(), fade)
        painter.end()


class PtitBrand(QWidget):
    """Stacked logo and bilingual name shared by every sidebar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(170)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 8, 6)
        layout.setSpacing(4)
        logo_label = QLabel()
        logo_label.setFixedSize(58, 74)
        logo = QPixmap(str(IMAGES / "ptit_logo.png"))
        if not logo.isNull():
            width, height = logo.width(), logo.height()
            logo = logo.copy(round(width * .312), round(height * .235),
                             round(width * .372), round(height * .468))
            logo.setMask(logo.createMaskFromColor(QColor("white"), Qt.MaskMode.MaskInColor))
            logo_label.setPixmap(logo.scaled(
                58, 74, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
        layout.addWidget(logo_label, 0, Qt.AlignmentFlag.AlignLeft)
        self.subtitle = QLabel("QUẢN LÝ TÍN CHỈ\nVÀ SINH VIÊN")
        self.subtitle.setObjectName("brandSubtitle")
        self.subtitle.setStyleSheet(
            'color: #e0f1ff; background: transparent; border: none; '
            'font-family: "Segoe UI"; font-size: 13px; font-weight: 700;'
        )
        layout.addWidget(self.subtitle)
        self.english_name = QLabel(
            "Posts and Telecommunications\nInstitute of Technology"
        )
        self.english_name.setObjectName("brandEnglish")
        self.english_name.setStyleSheet(
            'color: #7eb9df; background: transparent; border: none; '
            'font-family: "Segoe UI"; font-size: 9px; font-weight: 400;'
        )
        layout.addWidget(self.english_name)
        layout.addStretch()
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: rgba(157, 210, 255, 100); border: none;")
        layout.addWidget(separator)


class SidebarNavButton(QPushButton):
    """Roomy navigation with a shared hover, pressed and selected appearance."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._keyboard_focus = False
        self.setCheckable(True)
        self.setFixedHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setStyleSheet(
            'font-family: "Segoe UI"; font-size: 14px; '
            'background: transparent; border: none; padding: 0; '
            'min-height: 48px; max-height: 48px;'
        )

    def enterEvent(self, event):
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.update()

    def focusInEvent(self, event):
        self._keyboard_focus = event.reason() in (
            Qt.FocusReason.TabFocusReason, Qt.FocusReason.BacktabFocusReason,
            Qt.FocusReason.ShortcutFocusReason,
        )
        super().focusInEvent(event)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bounds = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        selected = self.isChecked()
        if selected or self.isDown():
            fill = QLinearGradient(0, 0, self.width(), self.height())
            fill.setColorAt(0, QColor("#159dff" if not self.isDown() else "#087acf"))
            fill.setColorAt(1, QColor("#086bd8"))
            painter.setBrush(fill)
            painter.setPen(QPen(QColor("#42afff"), 1))
            painter.drawRoundedRect(bounds, 7, 7)
        elif self.underMouse():
            painter.setBrush(QColor(29, 133, 236, 95))
            painter.setPen(QPen(QColor(110, 192, 255, 90), 1))
            painter.drawRoundedRect(bounds, 7, 7)
        if selected:
            painter.setPen(Qt.PenStyle.NoPen)
            for width, alpha in ((9, 30), (6, 65), (3, 255)):
                painter.setBrush(QColor(185, 239, 255, alpha))
                painter.drawRoundedRect(QRectF(3, 10, width, self.height() - 20), 1.5, 1.5)
            painter.setPen(QPen(QColor("#e8f7ff"), 1.7,
                                Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            x, y = self.width() - 18, self.height() / 2
            painter.drawLine(QPointF(x - 3, y - 4), QPointF(x + 1, y))
            painter.drawLine(QPointF(x + 1, y), QPointF(x - 3, y + 4))
        self.icon().paint(painter, 14, (self.height() - 25) // 2, 25, 25)
        font = self.font()
        font.setBold(selected)
        painter.setFont(font)
        painter.setPen(QColor("#ffffff" if selected else "#dcecff"))
        painter.drawText(QRectF(53, 0, self.width() - 80, self.height()),
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         self.text())
        if self.hasFocus() and self._keyboard_focus:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor("#c4e8ff"), 1, Qt.PenStyle.DotLine))
            painter.drawRoundedRect(bounds.adjusted(3, 3, -3, -3), 5, 5)
        painter.end()
