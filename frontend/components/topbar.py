from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)


class TopBar(QFrame):
    search_changed = pyqtSignal(str)
    logout_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(70)
        self.setObjectName("topbar")

        self.setStyleSheet("""
            #topbar {
                background-color: #ffffff;
                border-bottom: 1px solid #e2e8f0;
            }

            #topbar QLabel#topbarMenu {
                font-size: 24px;
                color: #28445f;
                background: transparent;
            }

            #topbar QLineEdit#topbarSearch {
                background-color: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 18px;
                padding: 8px 16px;
                font-size: 13px;
                color: #0f172a;
            }

            #topbar QLineEdit#topbarSearch:focus {
                border: 1.5px solid #2d7dd2;
                background-color: #ffffff;
            }

            #topbar QPushButton#topbarNotif {
                border: none;
                background: transparent;
                font-size: 18px;
                padding: 4px;
                border-radius: 6px;
            }

            #topbar QPushButton#topbarNotif:hover {
                background-color: #f1f5f9;
            }

            #topbar QLabel#topbarUser {
                font-size: 14px;
                font-weight: 600;
                color: #0f2b4c;
            }

            #topbar QPushButton#topbarLogout {
                border: none;
                background: transparent;
                font-size: 13px;
                color: #64748b;
                padding: 6px 12px;
                border-radius: 6px;
            }

            #topbar QPushButton#topbarLogout:hover {
                color: #ef4444;
                background-color: #fef2f2;
            }
        """)

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(22, 10, 22, 10)
        layout.setSpacing(15)

        menu_label = QLabel("☰")
        menu_label.setObjectName("topbarMenu")

        self.search_input = QLineEdit()
        self.search_input.setObjectName("topbarSearch")
        self.search_input.setPlaceholderText("Tìm kiếm chức năng...")
        self.search_input.setFixedWidth(360)

        self.search_input.textChanged.connect(
            self.search_changed.emit
        )

        notification_button = QPushButton("🔔")
        notification_button.setObjectName("topbarNotif")

        user_label = QLabel("Admin")
        user_label.setObjectName("topbarUser")

        logout_button = QPushButton("Đăng xuất")
        logout_button.setObjectName("topbarLogout")

        logout_button.clicked.connect(
            self.logout_clicked.emit
        )

        layout.addWidget(menu_label)
        layout.addWidget(self.search_input)

        layout.addStretch()

        layout.addWidget(notification_button)
        layout.addWidget(user_label)
        layout.addWidget(logout_button)