"""Reusable non-modal forms and an animated right-hand editor."""
from PyQt6.QtCore import QEasingCurve, Qt, QVariantAnimation, pyqtSignal
from PyQt6.QtWidgets import (
    QDialogButtonBox, QFormLayout, QFrame, QHBoxLayout, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)


class EditorForm(QWidget):
    accepted = pyqtSignal()
    rejected = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.on_save = None

    def accept(self):
        # Backend failures leave the form and its current input in place.
        if self.on_save is None or self.on_save():
            self.accepted.emit()

    def reject(self):
        self.rejected.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            buttons = self.findChild(QDialogButtonBox)
            buttons.button(QDialogButtonBox.StandardButton.Save).click()
            event.accept()
        else:
            super().keyPressEvent(event)

    def prepare_panel(self):
        """Reuse the controls/validators in a fixed header, scrolling body and footer."""
        root = self.layout()
        items = []
        while root.count():
            items.append(root.takeAt(0))
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        header = QWidget()
        heading = QHBoxLayout(header)
        heading.setContentsMargins(18, 14, 12, 14)
        title = items.pop(0).widget()
        title.setWordWrap(True)
        heading.addWidget(title, 1)
        close = QPushButton("×")
        close.setObjectName("panelCloseButton")
        close.setAccessibleName("Đóng biểu mẫu")
        close.setToolTip("Đóng (Esc)")
        close.setFixedSize(30, 30)
        close.clicked.connect(self.reject)
        heading.addWidget(close)
        root.addWidget(header)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(18, 8, 18, 18)
        body_layout.setSpacing(12)
        buttons = None
        for item in items:
            if isinstance(item.widget(), QDialogButtonBox):
                buttons = item.widget()
            elif item.layout() is not None:
                form = item.layout()
                if isinstance(form, QFormLayout):
                    form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
                    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
                    form.setVerticalSpacing(8)
                body_layout.addLayout(form)
            elif item.widget() is not None:
                body_layout.addWidget(item.widget())
        body_layout.addStretch()
        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setWidget(body)
        root.addWidget(scroll, 1)
        footer = QWidget()
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(18, 12, 18, 16)
        footer_layout.addWidget(buttons)
        root.addWidget(footer)
        self.setStyleSheet(self.styleSheet() + """
            QWidget#subjectDialog { background: white; }
            QScrollArea, QScrollArea > QWidget > QWidget { background: white; border: none; }
            QLabel#dialogTitle { font-size: 18px; }
            QPushButton#panelCloseButton {
                border: none; background: transparent; color: #365b8d;
                padding: 0; min-width: 0; min-height: 0; font-size: 24px;
            }
            QPushButton#panelCloseButton:hover { background: #edf6ff; }
            QLineEdit, QComboBox, QSpinBox { min-height: 24px; font-size: 13px; }
        """)


class EditorPanelHost(QWidget):
    """Resize the list on wide screens and overlay it on narrow screens."""
    PANEL_WIDTH = 390

    def __init__(self, content, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content = content
        content.setParent(self)
        self.form = None
        self._progress = 0.0
        self._closing = False
        self.panel = QFrame(self)
        self.panel.setObjectName("editorPanel")
        self.panel.setStyleSheet("QFrame#editorPanel { background: white; border-left: 1px solid #d8e2ef; }")
        self.panel_layout = QVBoxLayout(self.panel)
        self.panel_layout.setContentsMargins(1, 0, 0, 0)
        self.panel.hide()
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(230)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.valueChanged.connect(self._animate)
        self.animation.finished.connect(self._finished)

    def open_form(self, form, on_save=None):
        self.animation.stop()
        self._discard_form()
        self.form = form
        form.on_save = on_save
        form.prepare_panel()
        form.accepted.connect(self.close_panel)
        form.rejected.connect(self.close_panel)
        self.panel_layout.addWidget(form)
        self._closing = False
        self.panel.show()
        self.panel.raise_()
        form.show()
        self.animation.setStartValue(self._progress)
        self.animation.setEndValue(1.0)
        self.animation.start()
        form.focusNextChild()

    def close_panel(self, immediate=False):
        self.animation.stop()
        self._closing = True
        if immediate:
            self._animate(0.0)
            self._finished()
        else:
            self.animation.setStartValue(self._progress)
            self.animation.setEndValue(0.0)
            self.animation.start()

    def _discard_form(self):
        if self.form is not None:
            self.panel_layout.removeWidget(self.form)
            self.form.hide()
            self.form.deleteLater()
            self.form = None

    def _animate(self, value):
        self._progress = float(value)
        self._position_widgets()

    def _finished(self):
        if self._closing:
            self.panel.hide()
            self._discard_form()

    def _position_widgets(self):
        width = min(self.PANEL_WIDTH, self.width())
        revealed = round(width * self._progress)
        minimum_content = max(820, self.content.widget().minimumSizeHint().width())
        self.overlay = self.width() < minimum_content + width
        self.content.setGeometry(0, 0, self.width() - (0 if self.overlay else revealed), self.height())
        self.panel.setGeometry(self.width() - revealed, 0, width, self.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_widgets()

    def hideEvent(self, event):
        self.close_panel(immediate=True)
        super().hideEvent(event)
