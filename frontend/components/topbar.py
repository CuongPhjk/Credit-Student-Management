"""Compact header shared by all application pages."""
from PyQt6.QtWidgets import QHBoxLayout, QLabel

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
        self.setStyleSheet("""
            QFrame#topbar { background: transparent; border: none; }
            QLabel#topbarTitle { background: transparent; color: #12345b; font-size: 21px; font-weight: 700; }
        """)
