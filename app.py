"""Điểm khởi chạy ứng dụng quản lý tín chỉ sinh viên."""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from frontend.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    style_path = Path(__file__).resolve().parent / "frontend" / "resources" / "styles" / "ptit.qss"
    if style_path.exists():
        app.setStyleSheet(style_path.read_text(encoding="utf-8"))
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
