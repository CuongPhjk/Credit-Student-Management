"""Compact header shared by all application pages."""
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QToolButton

from frontend.components.branding import CampusBackground


class TopBar(CampusBackground):
    def __init__(self, parent=None):
        super().__init__(parent, header=True)
        self.setObjectName("topbar")
        self.setFixedHeight(56)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        title = QLabel("PTIT - HỆ THỐNG QUẢN LÝ ĐÀO TẠO")
        title.setObjectName("topbarTitle")
        layout.addWidget(title)
        layout.addStretch()
        self.undo_button = QToolButton(self)
        self.undo_button.setObjectName("undoButton")
        self.undo_button.hide()
        layout.addWidget(self.undo_button)
        self.setStyleSheet("""
            QFrame#topbar { background: transparent; border: none; }
            QLabel#topbarTitle { background: transparent; color: #12345b; font-size: 21px; font-weight: 700; }
            QToolButton#undoButton {
                padding: 6px 12px; border: 1px solid #b9cce3;
                border-radius: 6px; background: white; color: #244f82;
                font-size: 13px; font-weight: 600;
            }
            QToolButton#undoButton:hover { background: #edf6ff; }
            QToolButton#undoButton:disabled { color: #7c8a9c; background: #f3f5f8; }
        """)

    def set_undo_action(self, action):
        self.undo_button.setDefaultAction(action)
        self.undo_button.show()
