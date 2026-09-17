from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
)


class SearchBox(QFrame):
    """
    Component ô tìm kiếm hiện đại có tích hợp icon, nút xóa nhanh (clear),
    hỗ trợ phím Enter và cơ chế debounce (chờ người dùng gõ xong).
    """

    text_changed = pyqtSignal(str)
    search_submitted = pyqtSignal(str)
    cleared = pyqtSignal()

    def __init__(
        self,
        placeholder="Tìm kiếm...",
        parent=None,
        debounce_ms=300,
        width=None,
    ):
        super().__init__(parent)

        self.debounce_ms = debounce_ms
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._on_debounce_timeout)

        self.setObjectName("searchBoxFrame")
        if width:
            self.setFixedWidth(width)
        else:
            self.setMinimumWidth(220)

        self.setFixedHeight(38)

        self.setStyleSheet("""
            #searchBoxFrame {
                background-color: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 19px;
            }

            #searchBoxFrame:focus-within {
                border: 1.5px solid #2d7dd2;
                background-color: #ffffff;
            }

            QLabel#searchIcon {
                color: #64748b;
                font-size: 13px;
                background: transparent;
                border: none;
            }

            QLineEdit#searchInput {
                border: none;
                background: transparent;
                font-size: 13px;
                color: #0f172a;
                padding: 0px 4px;
            }

            QPushButton#clearButton {
                border: none;
                background: transparent;
                color: #94a3b8;
                font-size: 12px;
                font-weight: bold;
                border-radius: 10px;
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
            }

            QPushButton#clearButton:hover {
                background-color: #e2e8f0;
                color: #334155;
            }
        """)

        self.init_ui(placeholder)

    def init_ui(self, placeholder):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 10, 0)
        layout.setSpacing(6)

        self.icon_label = QLabel("🔍")
        self.icon_label.setObjectName("searchIcon")

        self.input_field = QLineEdit()
        self.input_field.setObjectName("searchInput")
        self.input_field.setPlaceholderText(placeholder)

        self.clear_button = QPushButton("✕")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_button.setVisible(False)

        # Signals
        self.input_field.textChanged.connect(self._handle_text_changed)
        self.input_field.returnPressed.connect(self._handle_return_pressed)
        self.clear_button.clicked.connect(self.clear)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.clear_button)

    def _handle_text_changed(self, text: str):
        self.clear_button.setVisible(bool(text))
        if self.debounce_ms > 0:
            self._debounce_timer.start(self.debounce_ms)
        else:
            self.text_changed.emit(text)

    def _on_debounce_timeout(self):
        self.text_changed.emit(self.text())

    def _handle_return_pressed(self):
        self._debounce_timer.stop()
        self.search_submitted.emit(self.text())

    def text(self) -> str:
        return self.input_field.text().strip()

    def set_text(self, text: str):
        self.input_field.setText(text)

    def clear(self):
        self.input_field.clear()
        self.cleared.emit()
        self.text_changed.emit("")

    def set_placeholder(self, placeholder: str):
        self.input_field.setPlaceholderText(placeholder)

    def set_focus(self):
        self.input_field.setFocus()
