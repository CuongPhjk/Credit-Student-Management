"""Điểm khởi chạy ứng dụng quản lý tín chỉ sinh viên."""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from frontend.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    resources_path = Path(__file__).resolve().parent / "frontend" / "resources"
    style_path = resources_path / "styles" / "ptit.qss"
    if style_path.exists():
        stylesheet = style_path.read_text(encoding="utf-8")
        icons_path = resources_path / "icons"
        stylesheet = stylesheet.replace(
            "__CHEVRON_DOWN_ICON__", (icons_path / "chevron_down.svg").as_posix()
        ).replace(
            "__CHEVRON_UP_ICON__", (icons_path / "chevron_up.svg").as_posix()
        )
        app.setStyleSheet(stylesheet)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
