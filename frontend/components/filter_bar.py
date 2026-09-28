from pathlib import Path

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
)

from .search_box import SearchBox


class FilterBar(QFrame):
    """
    Thanh lọc dữ liệu (Filter Bar) linh hoạt hỗ trợ thêm combobox,
    ô tìm kiếm, nút lọc, nút đặt lại và các nút hành động (thêm, xuất, v.v.).
    """

    filter_changed = pyqtSignal(dict)
    filter_applied = pyqtSignal(dict)
    filter_reset = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controls = {}
        self.labels = {}
        self.buttons = {}

        self.setObjectName("filterBar")
        chevron_path = (
            Path(__file__).resolve().parents[1] / "resources" / "icons" / "chevron_down.svg"
        ).as_posix()
        stylesheet = """
            #filterBar {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 4px;
            }

            #filterBar QLabel {
                color: #334155;
                font-size: 13px;
                font-weight: 600;
            }

            #filterBar QComboBox {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                color: #0f172a;
                min-height: 22px;
            }

            #filterBar QComboBox:focus {
                border: 1.5px solid #2d7dd2;
            }

            #filterBar QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 28px;
                border: none;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                background: transparent;
            }

            #filterBar QComboBox::down-arrow {
                image: url("__CHEVRON_DOWN_ICON__");
                border: none;
                width: 20px;
                height: 14px;
            }

            #filterBar QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                selection-background-color: #dcecff;
                selection-color: #0f2b4c;
                padding: 4px;
            }

            #filterBar QPushButton {
                padding: 7px 16px;
                font-size: 13px;
                font-weight: 500;
                border-radius: 6px;
                min-height: 20px;
            }

            #filterBar QPushButton#btn-primary, #filterBar QPushButton#btnPrimary {
                background-color: #2d7dd2;
                border: 1px solid #2d7dd2;
                color: #ffffff;
                font-weight: 600;
            }

            #filterBar QPushButton#btn-primary:hover, #filterBar QPushButton#btnPrimary:hover {
                background-color: #1d68b8;
                border-color: #1d68b8;
            }

            #filterBar QPushButton#btn-secondary, #filterBar QPushButton#btnSecondary {
                background-color: #eef2f7;
                border: 1px solid #d3dde8;
                color: #26384d;
            }

            #filterBar QPushButton#btn-secondary:hover, #filterBar QPushButton#btnSecondary:hover {
                background-color: #e1e7ee;
                border-color: #c4d1df;
                color: #0f172a;
            }

            #filterBar QPushButton#btn-success, #filterBar QPushButton#btnSuccess {
                background-color: #10b981;
                border: 1px solid #10b981;
                color: #ffffff;
                font-weight: 600;
            }

            #filterBar QPushButton#btn-success:hover, #filterBar QPushButton#btnSuccess:hover {
                background-color: #059669;
                border-color: #059669;
            }

            #filterBar QPushButton#btn-danger, #filterBar QPushButton#btnDanger {
                background-color: #ef4444;
                border: 1px solid #ef4444;
                color: #ffffff;
                font-weight: 600;
            }

            #filterBar QPushButton#btn-danger:hover, #filterBar QPushButton#btnDanger:hover {
                background-color: #dc2626;
                border-color: #dc2626;
            }

            #filterBar QPushButton#btn-ptit, #filterBar QPushButton#btnPtit {
                background-color: #c8102e;
                border: 1px solid #c8102e;
                color: #ffffff;
                font-weight: 600;
            }

            #filterBar QPushButton#btn-ptit:hover, #filterBar QPushButton#btnPtit:hover {
                background-color: #a60d25;
                border-color: #a60d25;
            }
        """
        self.setStyleSheet(stylesheet.replace("__CHEVRON_DOWN_ICON__", chevron_path))

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(14, 10, 14, 10)
        self.layout.setSpacing(12)

    def add_combobox(
        self,
        key: str,
        label_text: str = "",
        items: list = None,
        default_index: int = 0,
        width: int = 140,
    ) -> QComboBox:
        """Thêm combobox chọn lọc (ví dụ: Niên khóa, Học kỳ, Lớp, v.v.)."""
        if items is None:
            items = []

        if label_text:
            label = QLabel(label_text)
            self.labels[key] = label
            self.layout.addWidget(label)

        combo = QComboBox()
        combo.setFixedWidth(width)
        combo.addItems([str(item) for item in items])
        if 0 <= default_index < len(items):
            combo.setCurrentIndex(default_index)

        combo.currentIndexChanged.connect(lambda _: self._emit_filter_changed())

        self.controls[key] = ("combobox", combo, default_index)
        self.layout.addWidget(combo)
        return combo

    def add_search(
        self,
        key: str = "search",
        placeholder: str = "Tìm kiếm...",
        width: int = 240,
    ) -> SearchBox:
        """Thêm ô tìm kiếm với SearchBox component."""
        search = SearchBox(placeholder=placeholder, width=width)
        search.text_changed.connect(lambda _: self._emit_filter_changed())
        search.search_submitted.connect(lambda _: self.filter_applied.emit(self.get_filter_values()))

        self.controls[key] = ("search", search, "")
        self.layout.addWidget(search)
        return search

    def add_button(
        self,
        text: str,
        key: str = None,
        style_type: str = "primary",
        on_click=None,
    ) -> QPushButton:
        """Thêm nút hành động (style_type: 'primary', 'secondary', 'success', 'danger')."""
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setObjectName(f"btn-{style_type}")

        if on_click:
            btn.clicked.connect(on_click)

        if key:
            self.buttons[key] = btn

        self.layout.addWidget(btn)
        return btn

    def add_apply_button(self, text: str = "Lọc") -> QPushButton:
        """Nút kích hoạt phát tín hiệu filter_applied."""
        btn = self.add_button(text, key="apply", style_type="primary")
        btn.clicked.connect(lambda: self.filter_applied.emit(self.get_filter_values()))
        return btn

    def add_reset_button(self, text: str = "Đặt lại") -> QPushButton:
        """Nút đặt lại tất cả bộ lọc về mặc định."""
        btn = self.add_button(text, key="reset", style_type="secondary")
        btn.clicked.connect(self.reset_all)
        return btn

    def add_stretch(self):
        """Thêm khoảng dãn cách linh hoạt."""
        self.layout.addStretch()

    def add_spacing(self, spacing: int):
        """Thêm khoảng cách cố định giữa các thành phần."""
        self.layout.addSpacing(spacing)

    def set_combobox_items(self, key: str, items: list, default_index: int = 0):
        """Cập nhật lại danh sách lựa chọn cho một combobox."""
        if key in self.controls and self.controls[key][0] == "combobox":
            combo = self.controls[key][1]
            combo.blockSignals(True)
            combo.clear()
            combo.addItems([str(item) for item in items])
            if 0 <= default_index < len(items):
                combo.setCurrentIndex(default_index)
            combo.blockSignals(False)

    def get_filter_values(self) -> dict:
        """Lấy toàn bộ giá trị hiện tại của các bộ lọc dưới dạng dictionary."""
        values = {}
        for key, (ctrl_type, ctrl, _) in self.controls.items():
            if ctrl_type == "combobox":
                values[key] = ctrl.currentText()
            elif ctrl_type == "search":
                values[key] = ctrl.text()
        return values

    def get_value(self, key: str):
        """Lấy giá trị của một bộ lọc theo key."""
        if key in self.controls:
            ctrl_type, ctrl, _ = self.controls[key]
            if ctrl_type == "combobox":
                return ctrl.currentText()
            elif ctrl_type == "search":
                return ctrl.text()
        return None

    def set_value(self, key: str, value):
        """Thiết lập giá trị cho một bộ lọc theo key."""
        if key in self.controls:
            ctrl_type, ctrl, _ = self.controls[key]
            if ctrl_type == "combobox":
                index = ctrl.findText(str(value))
                if index >= 0:
                    ctrl.setCurrentIndex(index)
            elif ctrl_type == "search":
                ctrl.set_text(str(value))

    def reset_all(self):
        """Đặt lại tất cả các điều khiển về trạng thái ban đầu."""
        for _, (ctrl_type, ctrl, default) in self.controls.items():
            ctrl.blockSignals(True)
            if ctrl_type == "combobox":
                if isinstance(default, int) and default < ctrl.count():
                    ctrl.setCurrentIndex(default)
            elif ctrl_type == "search":
                ctrl.clear()
            ctrl.blockSignals(False)

        self.filter_reset.emit()
        self.filter_changed.emit(self.get_filter_values())

    def _emit_filter_changed(self):
        self.filter_changed.emit(self.get_filter_values())
