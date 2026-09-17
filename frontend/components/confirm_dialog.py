from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
)


class ConfirmDialog(QDialog):

    def __init__(
        self,
        title="Xác nhận",
        message="Bạn có chắc chắn muốn thực hiện thao tác này?",
        parent=None
    ):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setModal(True)

        self.setFixedSize(420, 210)

        self.setObjectName("confirmDialog")
        self.setStyleSheet("""
            QDialog#confirmDialog {
                background-color: #ffffff;
                border-radius: 10px;
            }

            QLabel#confirmIcon {
                font-size: 36px;
                color: #f59e0b;
                background: transparent;
            }

            QLabel#confirmMessage {
                color: #1e293b;
                font-size: 14px;
                background: transparent;
            }

            QPushButton {
                min-width: 110px;
                min-height: 38px;
                border-radius: 6px;
                font-size: 13px;
            }

            QPushButton#cancelButton {
                background-color: #eef2f7;
                color: #26384d;
                border: 1px solid #d3dde8;
                font-weight: 500;
            }

            QPushButton#cancelButton:hover {
                background-color: #e1e7ee;
                border-color: #c4d1df;
                color: #0f172a;
            }

            QPushButton#confirmButton {
                background-color: #ef4444;
                color: #ffffff;
                border: 1px solid #ef4444;
                font-weight: 600;
            }

            QPushButton#confirmButton:hover {
                background-color: #dc2626;
                border-color: #dc2626;
            }
        """)

        self.init_ui(message)

    def init_ui(self, message):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            30,
            25,
            30,
            25
        )

        layout.setSpacing(20)

        icon = QLabel("⚠")
        icon.setObjectName("confirmIcon")
        icon.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        message_label = QLabel(message)
        message_label.setObjectName("confirmMessage")
        message_label.setWordWrap(True)

        message_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        buttons = QHBoxLayout()

        cancel_button = QPushButton("Hủy")
        cancel_button.setObjectName("cancelButton")
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)

        confirm_button = QPushButton("Xác nhận")
        confirm_button.setObjectName("confirmButton")
        confirm_button.setCursor(Qt.CursorShape.PointingHandCursor)

        cancel_button.clicked.connect(
            self.reject
        )

        confirm_button.clicked.connect(
            self.accept
        )

        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(confirm_button)

        layout.addWidget(icon)
        layout.addWidget(message_label)
        layout.addStretch()
        layout.addLayout(buttons)

    @staticmethod
    def ask(
        parent,
        title,
        message
    ):
        dialog = ConfirmDialog(
            title,
            message,
            parent
        )

        return (
            dialog.exec()
            == QDialog.DialogCode.Accepted
        )