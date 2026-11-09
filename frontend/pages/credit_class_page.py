"""Trang quản lý lớp tín chỉ, đồng bộ giao diện với trang môn học."""

from datetime import date
import math

from PyQt6.QtCore import QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from frontend.components.confirm_dialog import ConfirmDialog
from frontend.components.editor_panel import EditorForm
from frontend.components.input_validation import (
    add_inline_validation,
    apply_text_validator,
    is_duplicate_error,
    show_field_error,
    show_temporary_message,
    subject_code_error,
)
from frontend.components.notification import Notification, NotificationBanner, NotificationType
from frontend.pages.dashboard_page import svg_label, svg_pixmap
from frontend.pages.subject_page import SubjectPage


ACADEMIC_YEAR_START_MONTH = 8


def current_academic_year(today=None):
    """Trả về niên khóa hiện tại theo ngày địa phương của hệ thống."""
    today = today or date.today()
    start_year = (
        today.year
        if today.month >= ACADEMIC_YEAR_START_MONTH
        else today.year - 1
    )
    return f"{start_year}-{start_year + 1}"


def academic_year_is_current_or_future(year, today=None):
    """Kiểm tra niên khóa hợp lệ và không cũ hơn niên khóa hiện tại."""
    parts = year.split("-")
    if (
        len(parts) != 2
        or not all(part.isdigit() and len(part) == 4 for part in parts)
        or int(parts[1]) != int(parts[0]) + 1
    ):
        return False
    current_start_year = int(current_academic_year(today).split("-")[0])
    return int(parts[0]) >= current_start_year


class SubjectComboBox(QComboBox):
    """Combobox chon mon hoc ho tro lay/dat theo ma mon hoc hoac nhan hien thi."""

    def setCurrentText(self, text):
        text_str = str(text).strip()
        index = self.findData(text_str)
        if index >= 0:
            self.setCurrentIndex(index)
            return
        for i in range(self.count()):
            item_text = self.itemText(i)
            if item_text == text_str or item_text.startswith(text_str + " - "):
                self.setCurrentIndex(i)
                return
        super().setCurrentText(text)


class CreditClassForm(EditorForm):
    """Form dùng chung để mở và cập nhật lớp tín chỉ."""

    def __init__(
        self, subject_codes, credit_class=None, parent=None, on_add=None
    ):
        super().__init__(parent)
        self._editing = credit_class is not None
        self._on_add = on_add
        self.setWindowTitle(
            "Cập nhật lớp tín chỉ" if self._editing else "Mở lớp tín chỉ"
        )
        self.setObjectName("subjectDialog")

        root = QVBoxLayout(self)
        root.setContentsMargins(26, 24, 26, 22)
        root.setSpacing(18)
        title = QLabel(self.windowTitle())
        title.setObjectName("dialogTitle")
        root.addWidget(title)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(13)
        self.subject_input = SubjectComboBox()
        self.subject_input.setEditable(False)
        for item in subject_codes:
            if isinstance(item, (tuple, list)):
                label, code = item
                self.subject_input.addItem(label, code)
            else:
                self.subject_input.addItem(str(item), str(item))
        self.subject_input.setPlaceholderText("Chọn mã môn học")
        self.subject_input.setCurrentIndex(-1)
        self.year_input = QLineEdit()
        self.year_input.setMaxLength(9)
        self.year_input.setPlaceholderText("Ví dụ: 2026-2027")
        apply_text_validator(self.year_input)
        self.semester_input = QSpinBox()
        self.semester_input.setRange(1, 3)
        self.group_input = QSpinBox()
        self.group_input.setRange(1, 999)
        self.minimum_input = QSpinBox()
        self.minimum_input.setRange(1, 999)
        self.minimum_input.setValue(20)
        self.maximum_input = QSpinBox()
        self.maximum_input.setRange(1, 999)
        self.maximum_input.setValue(50)
        self.subject_error = add_inline_validation(
            form,
            "Mã môn học",
            self.subject_input,
        )
        self.year_error = add_inline_validation(
            form, "Niên khóa", self.year_input
        )
        form.addRow("Học kỳ", self.semester_input)
        self.group_error = add_inline_validation(
            form,
            "Nhóm",
            self.group_input,
        )
        form.addRow("Sĩ số tối thiểu", self.minimum_input)
        form.addRow("Sĩ số tối đa", self.maximum_input)
        root.addLayout(form)
        if not self._editing:
            hint = QLabel("Niên khóa phải có dạng YYYY-YYYY và gồm hai năm liên tiếp.")
            hint.setObjectName("creditClassInputHint")
            hint.setWordWrap(True)
            root.addWidget(hint)

        self.status_label = QLabel()
        self.status_label.setObjectName("dialogStatus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.hide()
        root.addWidget(self.status_label)

        if credit_class is not None:
            self.subject_input.setCurrentText(credit_class.ma_mh)
            self.year_input.setText(credit_class.nien_khoa)
            self.semester_input.setValue(credit_class.hoc_ky)
            self.group_input.setValue(credit_class.nhom)
            self.minimum_input.setValue(credit_class.so_sv_min)
            self.maximum_input.setValue(credit_class.so_sv_max)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Save
        )
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Hủy")
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Lưu")
        buttons.button(QDialogButtonBox.StandardButton.Save).setObjectName(
            "saveButton"
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)
        self.setStyleSheet("""
            QWidget#subjectDialog { background: white; }
            QLabel#dialogTitle { color: #0f2b4c; font-size: 18px; font-weight: 700; }
            QLineEdit, QComboBox, QSpinBox { min-height: 28px; }
            QLineEdit[invalid="true"], QComboBox[invalid="true"],
            QSpinBox[invalid="true"] {
                border: 1px solid #dc2626;
            }
            QLabel#fieldError { color: #dc2626; font-size: 12px; }
            QLabel#creditClassInputHint { color: #64748b; font-size: 12px; }
            QLabel#dialogStatus[status="success"] {
                color: #15803d; background: #dcfce7; padding: 7px;
                border-radius: 5px; font-weight: 600;
            }
            QLabel#dialogStatus[status="error"] {
                color: #b91c1c; background: #fee2e2; padding: 7px;
                border-radius: 5px;
            }
            QPushButton#saveButton {
                color: white; background: #087cf0; border-color: #087cf0;
                min-width: 90px; font-weight: 600;
            }
            QPushButton#saveButton:hover { background: #076bd0; }
        """)

    def _selected_subject_code(self):
        data = self.subject_input.currentData()
        if data is not None and str(data).strip():
            return str(data).strip()
        text = self.subject_input.currentText().strip()
        if " - " in text:
            return text.split(" - ")[0].strip()
        return text

    def _validate(self):
        subject = self._selected_subject_code()
        if not subject:
            show_field_error(
                self.subject_input, self.subject_error, "Vui lòng chọn môn học."
            )
            return
        if error := subject_code_error(subject):
            show_field_error(self.subject_input, self.subject_error, error)
            return
        if not self.group_input.text().strip():
            show_field_error(
                self.group_input, self.group_error, "Vui lòng nhập nhóm."
            )
            self.group_input.setFocus()
            return
        year = self.year_input.text().strip()
        parts = year.split("-")
        if (
            len(parts) != 2
            or not all(part.isdigit() and len(part) == 4 for part in parts)
            or int(parts[1]) != int(parts[0]) + 1
        ):
            show_field_error(
                self.year_input, self.year_error,
                "Niên khóa phải có dạng YYYY-YYYY và gồm hai năm liên tiếp.",
            )
            self.year_input.setFocus()
            return
        current_year = current_academic_year()
        if not academic_year_is_current_or_future(year):
            show_field_error(
                self.year_input, self.year_error,
                "Niên khóa không được cũ hơn niên khóa hiện tại "
                f"{current_year}.",
            )
            self.year_input.setFocus()
            return
        if self.minimum_input.value() > self.maximum_input.value():
            QMessageBox.warning(
                self,
                "Sĩ số không hợp lệ",
                "Sĩ số tối thiểu không được lớn hơn sĩ số tối đa.",
            )
            self.minimum_input.setFocus()
            return
        if self._editing or self._on_add is None:
            self.accept()
            return
        success, message, duplicate = self._on_add(self.values())
        if not success:
            if duplicate:
                show_field_error(self.group_input, self.group_error, message)
                self.group_input.setFocus()
                return
            show_temporary_message(
                self.status_label, message, status="error", duration=1500
            )
            return
        self._reset_for_next()
        show_temporary_message(self.status_label, message)

    def _reset_for_next(self):
        self.subject_input.setCurrentIndex(-1)
        self.year_input.clear()
        self.semester_input.setValue(1)
        self.group_input.setValue(1)
        self.minimum_input.setValue(20)
        self.maximum_input.setValue(50)
        self.subject_input.setFocus()

    def values(self):
        return (
            self._selected_subject_code(),
            self.year_input.text(),
            self.semester_input.value(),
            self.group_input.value(),
            self.minimum_input.value(),
            self.maximum_input.value(),
        )


class CreditClassTable(QTableWidget):
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    open_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        headers = [
            "Mã lớp tín chỉ", "Mã môn học", "Tên môn học",
            "Tối thiểu", "Tối đa", "Trạng thái", "Thao tác",
        ]
        super().__init__(0, len(headers), parent)
        self.setHorizontalHeaderLabels(headers)
        self.verticalHeader().hide()
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMinimumHeight(280)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for column in (0, 1, 3, 4, 5, 6):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
        widths = {
            0: 104, 1: 94, 3: 66, 4: 60, 5: 118, 6: 90,
        }
        for column, width in widths.items():
            self.setColumnWidth(column, width)

        self.cellDoubleClicked.connect(self._open_row)
        self.empty_label = QLabel("Chưa có dữ liệu", self.viewport())
        self.empty_label.setObjectName("subjectEmptyLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        self._sync_empty_state()

    def _open_row(self, row, column):
        item = self.item(row, 0)
        if item is not None and column != 6:
            self.open_requested.emit(int(item.text()))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.empty_label.setGeometry(self.viewport().rect())

    def set_credit_classes(self, credit_classes, subject_names=None):
        subject_names = subject_names or {}
        self.setRowCount(0)
        for credit_class in credit_classes:
            row = self.rowCount()
            self.insertRow(row)
            status = credit_class.trang_thai
            values = [
                credit_class.ma_lop_tc,
                credit_class.ma_mh,
                subject_names.get(credit_class.ma_mh, credit_class.ma_mh),
                credit_class.so_sv_min,
                credit_class.so_sv_max,
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter | (Qt.AlignmentFlag.AlignLeft
                    if column == 2 else Qt.AlignmentFlag.AlignCenter)
                )
                self.setItem(row, column, item)
            self.setCellWidget(row, 5, self._status_widget(status))
            self.setCellWidget(
                row, 6, self._action_widget(credit_class.ma_lop_tc)
            )
            self.setRowHeight(row, 38)
        self._sync_empty_state()

    @staticmethod
    def _status_widget(status):
        colors = {
            "Đang mở": ("#dcfce7", "#15803d", "#86efac"),
            "Đang đăng ký": ("#dcfce7", "#15803d", "#86efac"),
            "Đã hủy": ("#fee2e2", "#dc2626", "#fca5a5"),
            "Lớp đã hủy": ("#fee2e2", "#dc2626", "#fca5a5"),
        }
        background, foreground, border = colors[status]
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 3, 4, 3)
        badge = QLabel(status)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setMinimumWidth(90)
        badge.setFixedHeight(26)
        badge.setStyleSheet(f"""
            QLabel {{
                color: {foreground}; background: {background};
                border: 1px solid {border}; border-radius: 12px;
                padding: 1px 10px; font-size: 12px; font-weight: 600;
            }}
        """)
        layout.addStretch()
        layout.addWidget(badge)
        layout.addStretch()
        return container

    def _action_widget(self, class_id):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(7)
        edit_button = QPushButton()
        edit_button.setObjectName("tableActionButton")
        edit_button.setToolTip("Cập nhật lớp tín chỉ")
        edit_button.setIcon(QIcon(svg_pixmap("edit.svg", "#27466f", 19)))
        delete_button = QPushButton()
        delete_button.setObjectName("tableActionButton")
        delete_button.setToolTip("Xóa lớp tín chỉ")
        delete_button.setIcon(QIcon(svg_pixmap("delete.svg", "#ef233c", 19)))
        for button in (edit_button, delete_button):
            button.setFixedSize(28, 28)
            button.setIconSize(QSize(19, 19))
            button.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_button.clicked.connect(
            lambda _checked=False: self.edit_requested.emit(class_id)
        )
        delete_button.clicked.connect(
            lambda _checked=False: self.delete_requested.emit(class_id)
        )
        layout.addStretch()
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        layout.addStretch()
        return widget

    def _sync_empty_state(self):
        self.empty_label.setVisible(self.rowCount() == 0)
        self.empty_label.raise_()


class RegistrationStudentTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 3, parent)
        self.empty_label = QLabel("Không có dữ liệu", self.viewport())
        self.empty_label.setObjectName("subjectEmptyLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.sync_empty_state()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.empty_label.setGeometry(self.viewport().rect())

    def sync_empty_state(self):
        self.empty_label.setGeometry(self.viewport().rect())
        self.empty_label.setVisible(self.rowCount() == 0)
        self.empty_label.raise_()


class CreditClassPage(SubjectPage):
    """CRUD lớp tín chỉ, tái sử dụng toàn bộ khung giao diện môn học."""

    credit_class_count_changed = pyqtSignal(int)
    PAGE_SIZE = 12

    def __init__(
        self,
        manager=None,
        credit_class_type=None,
        subject_manager=None,
        parent=None,
    ):
        self.registration_manager = None
        self.subject_manager = subject_manager
        super().__init__(manager, credit_class_type, parent)
        self.credit_class_type = credit_class_type
        self.select_page("credit_class", emit_signal=False)

    def _apply_style(self):
        super()._apply_style()
        self.setStyleSheet(self.styleSheet() + """
            QPushButton#secondaryButton {
                min-height: 26px; padding: 5px 12px; color: #087cf0;
                background: white; border: 1px solid #87bff5;
                border-radius: 6px; font-size: 14px;
            }
            QPushButton#secondaryButton:hover { background: #edf6ff; }
        """)

    def _build_content(self):
        content = QWidget()
        content.setObjectName("subjectContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(10)
        list_view = QWidget()
        list_layout = QVBoxLayout(list_view)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(10)
        list_layout.addWidget(self._build_filters())
        self.credit_class_delete_notice = NotificationBanner()
        layout.addWidget(self.credit_class_delete_notice)
        self.credit_class_delete_notice_timer = QTimer(self)
        self.credit_class_delete_notice_timer.setSingleShot(True)
        self.credit_class_delete_notice_timer.timeout.connect(
            self.credit_class_delete_notice.hide
        )
        self.registration_stack = QStackedWidget()
        list_layout.addWidget(self._build_table_card(), 1)
        self.registration_stack.addWidget(list_view)
        self.registration_stack.addWidget(self._build_registration_view())
        layout.addWidget(self.registration_stack, 1)
        return content

    def _build_filters(self):
        card = QFrame()
        card.setObjectName("subjectCard")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        self.search_input = QLineEdit()
        apply_text_validator(self.search_input)
        self.search_input.setObjectName("subjectSearchInput")
        self.search_input.setProperty("invalid", False)
        self.search_input.setPlaceholderText("Tìm mã lớp, mã hoặc tên môn...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        search_field = self._field("Tìm kiếm", self.search_input)
        search_field.setMinimumWidth(170)
        layout.addWidget(search_field, 2)
        search_button = QPushButton("Tìm kiếm")
        search_button.setObjectName("primaryButton")
        search_button.setIcon(QIcon(svg_pixmap("search.svg", "#ffffff", 20)))
        search_button.setIconSize(QSize(20, 20))
        search_button.clicked.connect(self.submit_search)
        layout.addWidget(search_button, 0, Qt.AlignmentFlag.AlignBottom)
        self.year_filter = QComboBox()
        self.year_filter.addItem("Tất cả", None)
        layout.addWidget(self._field("Niên khóa", self.year_filter), 1)
        self.group_filter = QComboBox()
        self.group_filter.addItem("Tất cả", None)
        layout.addWidget(self._field("Nhóm", self.group_filter), 1)
        self.semester_filter = QComboBox()
        self.semester_filter.addItem("Tất cả", None)
        for semester in range(1, 4):
            self.semester_filter.addItem(str(semester), semester)
        layout.addWidget(self._field("Học kỳ", self.semester_filter), 1)
        self._filter_boxes = (self.year_filter, self.group_filter, self.semester_filter)
        self.filter_button = QPushButton("Lọc")
        self.filter_button.setObjectName("primaryButton")
        self.filter_button.clicked.connect(self.submit_filters)
        layout.addWidget(self.filter_button, 0, Qt.AlignmentFlag.AlignBottom)
        return card

    def _build_table_card(self):
        card = QFrame()
        card.setObjectName("subjectCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        heading = QLabel("Danh sách lớp tín chỉ")
        heading.setObjectName("sectionTitle")
        heading_row = QHBoxLayout()
        heading_row.addWidget(heading)
        heading_row.addStretch()
        cancel_underfilled = QPushButton("Hủy lớp thiếu sĩ số")
        cancel_underfilled.setObjectName("secondaryButton")
        cancel_underfilled.clicked.connect(self.cancel_underfilled_classes)
        heading_row.addWidget(cancel_underfilled)
        add_button = QPushButton("Mở lớp tín chỉ")
        add_button.setObjectName("primaryButton")
        add_button.setIcon(QIcon(svg_pixmap("plus.svg", "#ffffff", 21)))
        add_button.setIconSize(QSize(21, 21))
        add_button.clicked.connect(self.add_credit_class)
        heading_row.addWidget(add_button)
        layout.addLayout(heading_row)
        self.table = CreditClassTable()
        self.table.open_requested.connect(self.open_registrations)
        self.table.edit_requested.connect(self.edit_credit_class)
        self.table.delete_requested.connect(self.delete_credit_class)
        layout.addWidget(self.table, 1)
        notice = QFrame()
        notice.setObjectName("infoBanner")
        notice_layout = QHBoxLayout(notice)
        notice_layout.setContentsMargins(12, 7, 12, 7)
        notice_layout.addWidget(svg_label("info.svg", "#278df0", 24))
        notice_layout.addWidget(QLabel(
            "<b>Lưu ý:</b> Không thể xóa lớp tín chỉ đã có sinh viên đăng ký."
        ), 1)
        layout.addWidget(notice)
        footer = QHBoxLayout()
        self.range_label = QLabel("Hiển thị 0 lớp tín chỉ")
        self.range_label.setObjectName("rangeLabel")
        footer.addWidget(self.range_label)
        footer.addStretch()
        self.pagination = QHBoxLayout()
        self.pagination.setSpacing(5)
        footer.addLayout(self.pagination)
        layout.addLayout(footer)
        return card

    def _build_registration_view(self):
        card = QFrame()
        card.setObjectName("subjectCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        toolbar = QHBoxLayout()
        back = QPushButton("Quay lại danh sách lớp tín chỉ")
        back.setObjectName("secondaryButton")
        back.clicked.connect(lambda: self.registration_stack.setCurrentIndex(0))
        toolbar.addWidget(back)
        self.registration_heading = QLabel("Danh sách sinh viên đăng ký")
        self.registration_heading.setObjectName("rangeLabel")
        toolbar.addStretch()
        layout.addLayout(toolbar)
        title = QLabel("Danh sách sinh viên đăng ký")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        self.registration_heading.setWordWrap(True)
        layout.addWidget(self.registration_heading)
        search_row = QHBoxLayout()
        search_row.setSpacing(10)
        self.registration_search_input = QLineEdit()
        apply_text_validator(self.registration_search_input)
        self.registration_search_input.setObjectName("subjectSearchInput")
        self.registration_search_input.setPlaceholderText("Tìm theo mã sinh viên hoặc tên...")
        self.registration_search_input.setClearButtonEnabled(True)
        search_row.addWidget(self.registration_search_input, 1)
        self.registration_search_button = QPushButton("Tìm kiếm")
        self.registration_search_button.setObjectName("primaryButton")
        self.registration_search_button.setIcon(QIcon(svg_pixmap("search.svg", "#ffffff", 20)))
        self.registration_search_button.setIconSize(QSize(20, 20))
        self.registration_search_button.clicked.connect(self.search_registrations)
        search_row.addWidget(self.registration_search_button)
        layout.addLayout(search_row)
        self._registration_students = []
        self._registration_class_cancelled = False
        self.registration_table = RegistrationStudentTable()
        self.registration_table.setHorizontalHeaderLabels(
            ["Mã sinh viên", "Họ tên", "Trạng thái"]
        )
        self.registration_table.verticalHeader().hide()
        self.registration_table.setAlternatingRowColors(True)
        self.registration_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.registration_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        header = self.registration_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for column in (0, 2):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
            self.registration_table.setColumnWidth(column, 160)
        self.registration_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.registration_table, 1)
        self.registration_count = QLabel("Hiển thị 0 sinh viên")
        self.registration_count.setObjectName("rangeLabel")
        layout.addWidget(self.registration_count)
        return card

    def open_registrations(self, class_id):
        try:
            students = self.registration_manager.lay_danh_sach_dang_ky(class_id)
            credit_class = self.manager.tim_lop_tin_chi(class_id) if self.manager else None
        except (AttributeError, RuntimeError, ValueError) as error:
            self.credit_class_delete_notice.set_message(str(error), NotificationType.ERROR)
            self.credit_class_delete_notice_timer.start(3000)
            return
        caption = f"Lớp tín chỉ {class_id}"
        if credit_class is not None:
            caption += (f" • {credit_class.ma_mh} • {credit_class.nien_khoa}"
                        f" • Học kỳ {credit_class.hoc_ky} • Nhóm {credit_class.nhom}")
        self.registration_heading.setText(caption)
        self._registration_class_cancelled = credit_class is not None and credit_class.huy_lop
        self._registration_students = students
        self.registration_search_input.clear()
        self._render_registrations(students)
        self.registration_stack.setCurrentIndex(1)

    def search_registrations(self):
        text = self.registration_search_input.text().strip().casefold()
        students = [student for student in self._registration_students
                    if not text or text in student["ma_sv"].casefold()
                    or text in student["ho_ten"].casefold()]
        self._render_registrations(students)

    def _render_registrations(self, students):
        self.registration_table.setRowCount(0)
        self.registration_table.setRowCount(len(students))
        for row, student in enumerate(students):
            if student["da_huy"]:
                status = "Đã hủy"
            elif self._registration_class_cancelled:
                status = "Lớp đã hủy"
            else:
                status = "Đang đăng ký"
            values = [student["ma_sv"], student["ho_ten"], status]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter |
                                      (Qt.AlignmentFlag.AlignLeft if col == 1
                                       else Qt.AlignmentFlag.AlignCenter))
                self.registration_table.setItem(row, col, item)
            self.registration_table.setCellWidget(
                row, 2, CreditClassTable._status_widget(values[2])
            )
            self.registration_table.setRowHeight(row, 42)
        self.registration_table.sync_empty_state()
        self.registration_count.setText(
            f"Hiển thị {len(students)} / {len(self._registration_students)} sinh viên"
        )

    def _all_credit_classes(self):
        if self.manager is None:
            return []
        return list(self.manager.lay_danh_sach_lop_tin_chi())

    def _subject_codes(self):
        if self.subject_manager is None:
            return []
        return [
            (f"{subject.ma_mh} - {subject.ten_mh}", subject.ma_mh)
            for subject in self.subject_manager.lay_danh_sach_mon_hoc()
        ]

    def refresh(self):
        self.registration_stack.setCurrentIndex(0)
        try:
            credit_classes = self._all_credit_classes()
        except (RuntimeError, ValueError) as error:
            Notification.error(self, str(error))
            credit_classes = []
        self.credit_class_count_changed.emit(len(credit_classes))
        self._source_credit_classes = credit_classes
        self.subject_names = {
            subject.ma_mh: subject.ten_mh
            for subject in (self.subject_manager.lay_danh_sach_mon_hoc()
                            if self.subject_manager is not None else [])
        }
        selected_group = self.group_filter.currentData()
        self.group_filter.blockSignals(True)
        self.group_filter.clear()
        self.group_filter.addItem("Tất cả", None)
        for group in sorted({item.nhom for item in credit_classes}):
            self.group_filter.addItem(str(group), group)
        self.group_filter.setCurrentIndex(max(0, self.group_filter.findData(selected_group)))
        self.group_filter.blockSignals(False)
        selected_year = self.year_filter.currentData()
        years = sorted({item.nien_khoa for item in credit_classes}, reverse=True)
        self.year_filter.blockSignals(True)
        self.year_filter.clear()
        self.year_filter.addItem("Tất cả", None)
        for year in years:
            self.year_filter.addItem(year, year)
        index = self.year_filter.findData(selected_year)
        self.year_filter.setCurrentIndex(max(0, index))
        self.year_filter.blockSignals(False)
        self.apply_filters(reset_page=False)

    def apply_filters(self, *_args, reset_page=True):
        if reset_page:
            self.current_page = 1
        text = self._submitted_search_text
        year, group, semester = self._submitted_filters or (None, None, None)
        self.filtered_credit_classes = [
            item for item in getattr(self, "_source_credit_classes", [])
            if (
                not text
                or text in str(item.ma_lop_tc).casefold()
                or text in item.ma_mh.casefold()
                or text in self.subject_names.get(item.ma_mh, "").casefold()
            )
            and (year is None or item.nien_khoa == year)
            and (semester is None or item.hoc_ky == semester)
            and (group is None or item.nhom == group)
        ]
        self._render_filtered_page()

    def _render_filtered_page(self):
        page_count = max(
            1, math.ceil(len(self.filtered_credit_classes) / self.PAGE_SIZE)
        )
        self.current_page = min(self.current_page, page_count)
        start = (self.current_page - 1) * self.PAGE_SIZE
        page_items = self.filtered_credit_classes[start:start + self.PAGE_SIZE]
        self.table.set_credit_classes(page_items, self.subject_names)
        if self.filtered_credit_classes:
            self.range_label.setText(
                f"Hiển thị {start + 1} – {start + len(page_items)} "
                f"của {len(self.filtered_credit_classes)} lớp tín chỉ"
            )
        else:
            self.range_label.setText("Hiển thị 0 lớp tín chỉ")
        self._render_pagination(page_count)

    def _new_credit_class(self, values):
        if self.credit_class_type is None:
            raise RuntimeError("Backend C++ chưa được build hoặc chưa được nạp.")
        return self.credit_class_type(*values)

    def add_credit_class(self):
        def submit(values):
            try:
                self.manager.them_lop_tin_chi(
                    self._new_credit_class(values)
                )
            except (AttributeError, RuntimeError, ValueError) as error:
                message = str(error)
                return False, message, is_duplicate_error(message)
            self.refresh()
            return True, "Đã mở lớp tín chỉ.", False

        self.editor_host.open_form(CreditClassForm(
            self._subject_codes(), parent=self, on_add=submit
        ))

    def edit_credit_class(self, class_id):
        try:
            credit_class = self.manager.tim_lop_tin_chi(class_id)
        except (AttributeError, RuntimeError, ValueError) as error:
            Notification.error(self, str(error))
            return
        if credit_class is None:
            Notification.warning(self, "Không tìm thấy lớp tín chỉ cần cập nhật.")
            return
        dialog = CreditClassForm(
            self._subject_codes(), credit_class, self
        )
        def save():
            try:
                self.manager.cap_nhat_lop_tin_chi(
                    class_id, self._new_credit_class(dialog.values())
                )
            except (RuntimeError, ValueError) as error:
                show_temporary_message(dialog.status_label, str(error), status="error", duration=4000)
                return False
            self.refresh()
            show_temporary_message(dialog.status_label, "Đã cập nhật lớp tín chỉ.")
            close_timer = QTimer(dialog)
            close_timer.setSingleShot(True)
            close_timer.timeout.connect(
                lambda: self.editor_host.close_panel()
                if self.editor_host.form is dialog else None
            )
            close_timer.start(850)
            return False

        self.editor_host.open_form(dialog, on_save=save)

    def cancel_underfilled_classes(self):
        year = self.year_filter.currentData()
        semester = self.semester_filter.currentData()
        notice = self.credit_class_delete_notice
        timer = self.credit_class_delete_notice_timer
        if year is None or semester is None:
            notice.set_message("Chọn một niên khóa và một học kỳ để hủy lớp.", NotificationType.WARNING)
            timer.start(3000)
            return
        try:
            rows = self.manager.lay_lop_thieu_si_so(year, semester)
            if not rows:
                notice.set_message("Không có lớp thiếu sĩ số trong học kỳ đã chọn.", NotificationType.INFO)
                timer.start(3000)
                return
            if not self.confirm_underfilled_classes(year, semester, rows):
                return
            self.manager.huy_lop_thieu_si_so(year, semester, [row[0] for row in rows])
        except (AttributeError, RuntimeError, ValueError) as error:
            notice.set_message(str(error), NotificationType.ERROR)
            timer.start(3000)
            return
        self.refresh()
        notice.set_message(f"Đã hủy {len(rows)} lớp tín chỉ thiếu sĩ số.", NotificationType.SUCCESS)
        timer.start(3000)

    def confirm_underfilled_classes(self, year, semester, rows):
        table = QTableWidget(len(rows), 5)
        table.setHorizontalHeaderLabels(["Mã lớp", "Môn học", "Nhóm", "Đã đăng ký", "Tối thiểu"])
        table.verticalHeader().hide()
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for index, (class_id, subject_code, group, registered, minimum) in enumerate(rows):
            name = self.subject_names.get(subject_code)
            subject = f"{subject_code} – {name}" if name else subject_code
            for column, value in enumerate((class_id, subject, group, registered, minimum)):
                table.setItem(index, column, QTableWidgetItem(str(value)))

        dialog = ConfirmDialog(
            "Hủy lớp tín chỉ thiếu sĩ số",
            f"Niên khóa {year}, học kỳ {semester} có {len(rows)} lớp thiếu sĩ số.",
            self,
            content=table,
            confirm_text=f"Hủy {len(rows)} lớp",
            cancel_text="Quay lại",
        )
        return dialog.exec() == QDialog.DialogCode.Accepted

    def delete_credit_class(self, class_id):
        if not ConfirmDialog.ask(
            self,
            "Xóa lớp tín chỉ",
            f"Bạn có chắc muốn xóa lớp tín chỉ {class_id}?",
        ):
            return
        try:
            self.manager.xoa_lop_tin_chi(class_id)
        except (AttributeError, RuntimeError, ValueError) as error:
            self.credit_class_delete_notice.set_message(
                str(error), NotificationType.ERROR
            )
            self.credit_class_delete_notice_timer.start(3000)
            return
        self.credit_class_delete_notice.set_message(
            "Đã xóa lớp tín chỉ.", NotificationType.SUCCESS
        )
        self.credit_class_delete_notice_timer.start(3000)
        self.refresh()


__all__ = [
    "CreditClassForm",
    "CreditClassPage",
    "CreditClassTable",
    "academic_year_is_current_or_future",
    "current_academic_year",
]
