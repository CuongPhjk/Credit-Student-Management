from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QPushButton,
    QLabel,
)


class Sidebar(QFrame):
    page_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.buttons = {}

        self.setFixedWidth(240)
        self.setObjectName("sidebar")

        self.setStyleSheet("""
            #sidebar {
                background-color: #12345b;
                border: none;
            }

            #sidebar QLabel {
                color: #ffffff;
            }

            #sidebar QLabel#sidebarTitle {
                font-size: 28px;
                font-weight: bold;
                color: #ff3b30;
            }

            #sidebar QLabel#sidebarSubtitle {
                font-size: 12px;
                color: #d8e4f3;
            }

            #sidebar QLabel#sidebarVersion {
                color: #9eb3cb;
                font-size: 11px;
            }

            #sidebar QPushButton {
                text-align: left;
                padding: 14px 18px;
                border: none;
                border-radius: 8px;
                color: #ffffff;
                font-size: 15px;
                background: transparent;
            }

            #sidebar QPushButton:hover {
                background-color: #1d4f86;
            }

            #sidebar QPushButton:checked {
                background-color: #2d7dd2;
                font-weight: 600;
            }
        """)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 20, 14, 20)
        layout.setSpacing(8)

        title = QLabel("PTIT")
        title.setObjectName("sidebarTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("QUẢN LÝ TÍN CHỈ")
        subtitle.setObjectName("sidebarSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(25)

        menu_items = [
            ("dashboard", "⌂  Trang chủ"),
            ("student", "👤  Sinh viên"),
            ("class", "👥  Lớp"),
            ("subject", "📘  Môn học"),
            ("credit_class", "▣  Lớp tín chỉ"),
            ("registration", "☑  Đăng ký học"),
            ("score", "✎  Nhập điểm"),
        ]

        for key, text in menu_items:
            button = QPushButton(text)
            button.setCheckable(True)

            button.clicked.connect(
                lambda checked, page=key: self.select_page(page)
            )

            self.buttons[key] = button
            layout.addWidget(button)

        layout.addStretch()

        version = QLabel("v1.0.0")
        version.setObjectName("sidebarVersion")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(version)

        self.select_page("dashboard")

    def select_page(self, page_name):
        for name, button in self.buttons.items():
            button.setChecked(name == page_name)

        self.page_changed.emit(page_name)