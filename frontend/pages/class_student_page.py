"""Trang quản lý lớp và danh sách liên kết sinh viên của từng lớp."""

import math

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QComboBox,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
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
    text_input_error,
)
from frontend.components.notification import Notification
from frontend.pages.dashboard_page import svg_label, svg_pixmap
from frontend.pages.subject_page import SubjectPage


class ClassForm(EditorForm):
    def __init__(self, class_item=None, parent=None, on_add=None):
        super().__init__(parent)
        self._editing = class_item is not None
        self._on_add = on_add
        self.setWindowTitle("Cập nhật lớp" if self._editing else "Thêm lớp")
        self.setObjectName("subjectDialog")
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 24, 26, 22)
        root.setSpacing(18)
        title = QLabel(self.windowTitle())
        title.setObjectName("dialogTitle")
        root.addWidget(title)
        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(14)
        self.code_input = QLineEdit()
        self.code_input.setMaxLength(15)
        self.code_input.setPlaceholderText("Ví dụ: D21CQCN01")
        apply_text_validator(self.code_input)
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(50)
        self.name_input.setPlaceholderText("Nhập tên lớp")
        apply_text_validator(self.name_input)
        self.code_error = add_inline_validation(
            form,
            "Mã lớp",
            self.code_input,
        )
        self.name_error = add_inline_validation(
            form,
            "Tên lớp",
            self.name_input,
        )
        root.addLayout(form)
        self.status_label = QLabel()
        self.status_label.setObjectName("dialogStatus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.hide()
        root.addWidget(self.status_label)
        if class_item is not None:
            self.code_input.setText(class_item.ma_lop)
            self.code_input.setReadOnly(True)
            self.name_input.setText(class_item.ten_lop)
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
        self._apply_dialog_style()

    def _apply_dialog_style(self):
        self.setStyleSheet("""
            QWidget#subjectDialog { background: white; }
            QLabel#dialogTitle { color: #0f2b4c; font-size: 18px; font-weight: 700; }
            QLineEdit, QComboBox { min-height: 28px; }
            QLineEdit[invalid="true"], QComboBox[invalid="true"] {
                border: 1px solid #dc2626;
            }
            QLabel#fieldError { color: #dc2626; font-size: 12px; }
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

    def _validate(self):
        code = self.code_input.text()
        name = self.name_input.text()
        has_error = False
        if not code.strip():
            show_field_error(self.code_input, self.code_error, "Vui lòng nhập mã lớp.")
            has_error = True
        elif error := text_input_error(code):
            show_field_error(self.code_input, self.code_error, f"Mã lớp {error}.")
            has_error = True
        if not name.strip():
            show_field_error(self.name_input, self.name_error, "Vui lòng nhập tên lớp.")
            has_error = True
        elif error := text_input_error(name):
            show_field_error(self.name_input, self.name_error, f"Tên lớp {error}.")
            has_error = True
        if has_error:
            return
        if self._editing or self._on_add is None:
            self.accept()
            return
        success, message, duplicate = self._on_add(self.values())
        if not success:
            if duplicate:
                show_field_error(self.code_input, self.code_error, message)
                self.code_input.setFocus()
                return
            show_temporary_message(
                self.status_label, message, status="error", duration=1500
            )
            return
        self._reset_for_next()
        show_temporary_message(self.status_label, message)

    def _reset_for_next(self):
        self.code_input.clear()
        self.name_input.clear()
        self.code_input.setFocus()

    def values(self):
        return self.code_input.text(), self.name_input.text()


class StudentForm(ClassForm):
    def __init__(self, student=None, parent=None, on_add=None):
        EditorForm.__init__(self, parent)
        self._editing = student is not None
        self._on_add = on_add
        self.setWindowTitle(
            "Cập nhật sinh viên" if self._editing else "Thêm sinh viên"
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
        self.code_input = QLineEdit()
        self.code_input.setMaxLength(15)
        self.code_input.setPlaceholderText("Ví dụ: N21DCCN001")
        apply_text_validator(self.code_input)
        self.surname_input = QLineEdit()
        self.surname_input.setMaxLength(40)
        self.surname_input.setPlaceholderText("Họ và tên đệm")
        apply_text_validator(self.surname_input)
        self.given_name_input = QLineEdit()
        self.given_name_input.setMaxLength(15)
        self.given_name_input.setPlaceholderText("Tên")
        apply_text_validator(self.given_name_input)
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Nam", "Nữ"])
        self.phone_input = QLineEdit()
        self.phone_input.setMaxLength(11)
        self.phone_input.setPlaceholderText("Số điện thoại từ 9 đến 11 chữ số")
        apply_text_validator(self.phone_input)
        self.student_code_error = add_inline_validation(
            form,
            "Mã sinh viên",
            self.code_input,
        )
        self.surname_error = add_inline_validation(
            form,
            "Họ",
            self.surname_input,
        )
        self.given_name_error = add_inline_validation(
            form,
            "Tên",
            self.given_name_input,
        )
        form.addRow("Giới tính", self.gender_input)
        self.phone_error = add_inline_validation(
            form,
            "Số điện thoại",
            self.phone_input,
        )
        root.addLayout(form)
        self.status_label = QLabel()
        self.status_label.setObjectName("dialogStatus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.hide()
        root.addWidget(self.status_label)
        if student is not None:
            self.code_input.setText(student.ma_sv)
            self.code_input.setReadOnly(True)
            self.surname_input.setText(student.ho)
            self.given_name_input.setText(student.ten)
            self.gender_input.setCurrentText(student.phai)
            self.phone_input.setText(student.so_dt)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Save
        )
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(
            "Hủy"
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Lưu")
        buttons.button(QDialogButtonBox.StandardButton.Save).setObjectName(
            "saveButton"
        )
        buttons.accepted.connect(self._validate_student)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)
        self._apply_dialog_style()

    def _validate_student(self):
        if not self._editing and not self.code_input.text().strip():
            self.reject()
            return
        fields = (
            (self.code_input, self.student_code_error, "Vui lòng nhập mã sinh viên."),
            (self.surname_input, self.surname_error, "Vui lòng nhập họ sinh viên."),
            (self.given_name_input, self.given_name_error, "Vui lòng nhập tên sinh viên."),
            (self.phone_input, self.phone_error, "Vui lòng nhập số điện thoại."),
        )
        has_error = False
        for widget, error_label, message in fields:
            if not widget.text().strip():
                show_field_error(widget, error_label, message)
                has_error = True
        for widget, error_label, label in (
            (self.surname_input, self.surname_error, "Họ"),
            (self.given_name_input, self.given_name_error, "Tên"),
        ):
            value = widget.text()
            if value and (error := text_input_error(value, allow_digits=False)):
                show_field_error(widget, error_label, f"{label} {error}.")
                has_error = True
        phone = self.phone_input.text().strip()
        if phone and (not phone.isdigit() or not 9 <= len(phone) <= 11):
            show_field_error(
                self.phone_input,
                self.phone_error,
                "Số điện thoại phải gồm từ 9 đến 11 chữ số.",
            )
            has_error = True
        if has_error:
            return
        if self._editing or self._on_add is None:
            self.accept()
            return
        success, message, duplicate = self._on_add(self.values())
        if not success:
            if duplicate:
                show_field_error(
                    self.code_input, self.student_code_error, message
                )
                self.code_input.setFocus()
                return
            show_temporary_message(
                self.status_label, message, status="error", duration=1500
            )
            return
        self._reset_student_for_next()
        show_temporary_message(self.status_label, message)

    def _reset_student_for_next(self):
        self.code_input.clear()
        self.surname_input.clear()
        self.given_name_input.clear()
        self.gender_input.setCurrentText("Nam")
        self.phone_input.clear()
        self.code_input.setFocus()

    def values(self):
        return (
            self.code_input.text(),
            self.surname_input.text(),
            self.given_name_input.text(),
            self.gender_input.currentText(),
            self.phone_input.text(),
        )


class ActionTable(QTableWidget):
    edit_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def _fit_page_rows(self):
        """Keep paginated rows visible without an inner vertical scrollbar."""
        capacity = ClassStudentPage.PAGE_SIZE if isinstance(self, ClassTable) else ClassStudentPage.STUDENT_PAGE_SIZE
        preferred_height = 37 if isinstance(self, ClassTable) else 36
        minimum = (capacity * 32 + self.horizontalHeader().height()
                   + 2 * self.frameWidth())
        if self.horizontalScrollBar().isVisible():
            minimum += self.horizontalScrollBar().height()
        if self.minimumHeight() != minimum:
            self.setMinimumHeight(minimum)
        row_height = max(32, min(preferred_height, self.viewport().height() // capacity))
        for row in range(self.rowCount()):
            if self.rowHeight(row) != row_height:
                self.setRowHeight(row, row_height)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit_page_rows()

    def _action_widget(self, key, edit_tooltip, delete_tooltip):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(7, 2, 7, 2)
        layout.setSpacing(8)
        edit_button = QPushButton()
        edit_button.setObjectName("tableActionButton")
        edit_button.setToolTip(edit_tooltip)
        edit_button.setIcon(QIcon(svg_pixmap("edit.svg", "#27466f", 19)))
        delete_button = QPushButton()
        delete_button.setObjectName("tableActionButton")
        delete_button.setToolTip(delete_tooltip)
        delete_button.setIcon(QIcon(svg_pixmap("delete.svg", "#ef233c", 19)))
        for button in (edit_button, delete_button):
            button.setFixedSize(28, 28)
            button.setIconSize(QSize(19, 19))
            button.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_button.clicked.connect(
            lambda _checked=False: self.edit_requested.emit(key)
        )
        delete_button.clicked.connect(
            lambda _checked=False: self.delete_requested.emit(key)
        )
        layout.addStretch()
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        layout.addStretch()
        return widget


class ClassTable(ActionTable):
    open_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        headers = ["STT", "Mã lớp", "Tên lớp", "Số sinh viên", "Thao tác"]
        super().__init__(0, len(headers), parent)
        self.setHorizontalHeaderLabels(headers)
        self._configure()
        self.cellDoubleClicked.connect(self._open_row)

    def _configure(self):
        self.verticalHeader().hide()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMinimumHeight(280)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for column in (0, 1, 3, 4):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(0, 65)
        self.setColumnWidth(1, 160)
        self.setColumnWidth(3, 140)
        self.setColumnWidth(4, 135)
        self.empty_label = QLabel("Chưa có dữ liệu", self.viewport())
        self.empty_label.setObjectName("subjectEmptyLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.empty_label.setGeometry(self.viewport().rect())

    def set_classes(self, classes, first_number=1):
        self.setRowCount(0)
        for offset, class_item in enumerate(classes):
            row = self.rowCount()
            self.insertRow(row)
            values = [
                first_number + offset,
                class_item.ma_lop,
                class_item.ten_lop,
                class_item.so_sinh_vien,
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                alignment = Qt.AlignmentFlag.AlignVCenter
                alignment |= (
                    Qt.AlignmentFlag.AlignLeft if column == 2
                    else Qt.AlignmentFlag.AlignCenter
                )
                item.setTextAlignment(alignment)
                self.setItem(row, column, item)
            self.setCellWidget(row, 4, self._action_widget(
                class_item.ma_lop, "Cập nhật lớp", "Xóa lớp"
            ))
            self.setRowHeight(row, 37)
        self._fit_page_rows()
        self.empty_label.setVisible(self.rowCount() == 0)
        self.empty_label.raise_()

    def _open_row(self, row, _column):
        item = self.item(row, 1)
        if item is not None:
            self.open_requested.emit(item.text())


class StudentTable(ActionTable):
    def __init__(self, parent=None):
        headers = [
            "STT", "Mã sinh viên", "Họ", "Tên", "Giới tính",
            "Số điện thoại", "Thao tác",
        ]
        super().__init__(0, len(headers), parent)
        self.setHorizontalHeaderLabels(headers)
        self.verticalHeader().hide()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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
        widths = {0: 58, 1: 145, 3: 100, 4: 95, 5: 145, 6: 125}
        for column, width in widths.items():
            self.setColumnWidth(column, width)
        self.empty_label = QLabel("Lớp chưa có sinh viên", self.viewport())
        self.empty_label.setObjectName("subjectEmptyLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.empty_label.setGeometry(self.viewport().rect())

    def set_students(self, students, first_number=1):
        self.setRowCount(0)
        for offset, student in enumerate(students):
            row = self.rowCount()
            self.insertRow(row)
            values = [
                first_number + offset, student.ma_sv, student.ho,
                student.ten, student.phai, student.so_dt,
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter
                    | (Qt.AlignmentFlag.AlignLeft if column == 2
                       else Qt.AlignmentFlag.AlignCenter)
                )
                self.setItem(row, column, item)
            self.setCellWidget(row, 6, self._action_widget(
                student.ma_sv, "Cập nhật sinh viên", "Xóa sinh viên"
            ))
            self.setRowHeight(row, 36)
        self._fit_page_rows()
        self.empty_label.setVisible(self.rowCount() == 0)
        self.empty_label.raise_()


class ClassStudentPage(SubjectPage):
    class_count_changed = pyqtSignal(int)
    student_count_changed = pyqtSignal(int)
    PAGE_SIZE = 15
    STUDENT_PAGE_SIZE = 15

    def __init__(self, manager=None, class_type=None, student_type=None, parent=None):
        self.class_type = class_type
        self.student_type = student_type
        self.selected_class_code = None
        self.current_student_page = 1
        super().__init__(manager, class_type, parent)
        self.select_page("student", emit_signal=False)

    def _build_content(self):
        content = QWidget()
        content.setObjectName("subjectContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(10)
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self._build_class_view())
        self.content_stack.addWidget(self._build_student_view())
        layout.addWidget(self.content_stack, 1)
        return content

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

    def _build_class_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        filter_card = QFrame()
        filter_card.setObjectName("subjectCard")
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(12, 10, 12, 10)
        filter_layout.setSpacing(10)
        self.search_input = QLineEdit()
        apply_text_validator(self.search_input)
        self.search_input.setObjectName("subjectSearchInput")
        self.search_input.setProperty("invalid", False)
        self.search_input.setPlaceholderText("Tìm theo mã lớp hoặc tên lớp...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.returnPressed.connect(self.submit_search)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        filter_layout.addWidget(self._field("Tìm kiếm", self.search_input), 1)
        search_button = QPushButton("Tìm kiếm")
        search_button.setObjectName("primaryButton")
        search_button.setIcon(QIcon(svg_pixmap("search.svg", "#ffffff", 20)))
        search_button.clicked.connect(self.submit_search)
        filter_layout.addWidget(search_button, 0, Qt.AlignmentFlag.AlignBottom)
        divider = QFrame()
        divider.setFixedSize(1, 42)
        divider.setStyleSheet("background: #d8e2ef; border: none;")
        filter_layout.addWidget(divider)
        add_button = QPushButton("Thêm lớp")
        add_button.setObjectName("primaryButton")
        add_button.setIcon(QIcon(svg_pixmap("plus.svg", "#ffffff", 21)))
        add_button.clicked.connect(self.add_class)
        filter_layout.addWidget(add_button, 0, Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(filter_card)

        card = QFrame()
        card.setObjectName("subjectCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(10)
        heading = QLabel("Danh sách lớp")
        heading.setObjectName("sectionTitle")
        card_layout.addWidget(heading)
        self.class_table = ClassTable()
        self.class_table.edit_requested.connect(self.edit_class)
        self.class_table.delete_requested.connect(self.delete_class)
        self.class_table.open_requested.connect(self.open_student_list)
        card_layout.addWidget(self.class_table, 1)
        hint = QLabel("Nhấp đúp vào một lớp để xem và quản lý sinh viên")
        hint.setObjectName("rangeLabel")
        card_layout.addWidget(hint)
        footer = QHBoxLayout()
        self.range_label = QLabel("Hiển thị 0 lớp")
        self.range_label.setObjectName("rangeLabel")
        footer.addWidget(self.range_label)
        footer.addStretch()
        self.pagination = QHBoxLayout()
        self.pagination.setSpacing(5)
        footer.addLayout(self.pagination)
        card_layout.addLayout(footer)
        layout.addWidget(card, 1)
        return view

    def _build_student_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        toolbar = QFrame()
        toolbar.setObjectName("subjectCard")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 10, 12, 10)
        back_button = QPushButton("Quay lại danh sách lớp")
        back_button.setObjectName("secondaryButton")
        back_button.clicked.connect(self.show_class_list)
        toolbar_layout.addWidget(back_button)
        titles = QVBoxLayout()
        self.student_heading = QLabel("Danh sách sinh viên")
        self.student_heading.setObjectName("sectionTitle")
        self.student_class_name = QLabel("")
        self.student_class_name.setObjectName("rangeLabel")
        titles.addWidget(self.student_heading)
        titles.addWidget(self.student_class_name)
        toolbar_layout.addLayout(titles)
        toolbar_layout.addStretch()
        add_button = QPushButton("Thêm sinh viên")
        add_button.setObjectName("primaryButton")
        add_button.setIcon(QIcon(svg_pixmap("plus.svg", "#ffffff", 21)))
        add_button.clicked.connect(self.add_student)
        toolbar_layout.addWidget(add_button)
        layout.addWidget(toolbar)

        card = QFrame()
        card.setObjectName("subjectCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(10)
        search_row = QHBoxLayout()
        self.student_search_input = QLineEdit()
        apply_text_validator(self.student_search_input)
        self.student_search_input.setPlaceholderText(
            "Tìm theo mã, họ tên hoặc số điện thoại..."
        )
        self.student_search_input.setClearButtonEnabled(True)
        self.student_search_input.textChanged.connect(self.apply_student_filter)
        search_row.addWidget(self.student_search_input, 1)
        card_layout.addLayout(search_row)
        self.student_table = StudentTable()
        self.student_table.edit_requested.connect(self.edit_student)
        self.student_table.delete_requested.connect(self.delete_student)
        card_layout.addWidget(self.student_table, 1)
        notice = QFrame()
        notice.setObjectName("infoBanner")
        notice_layout = QHBoxLayout(notice)
        notice_layout.setContentsMargins(12, 7, 12, 7)
        notice_layout.addWidget(svg_label("info.svg", "#278df0", 24))
        notice_layout.addWidget(QLabel(
            "Danh sách luôn được chèn đúng thứ tự tăng dần theo tên, họ và mã sinh viên."
        ), 1)
        card_layout.addWidget(notice)
        footer = QHBoxLayout()
        self.student_range_label = QLabel("Hiển thị 0 sinh viên")
        self.student_range_label.setObjectName("rangeLabel")
        footer.addWidget(self.student_range_label)
        footer.addStretch()
        self.student_pagination = QHBoxLayout()
        self.student_pagination.setSpacing(5)
        footer.addLayout(self.student_pagination)
        card_layout.addLayout(footer)
        layout.addWidget(card, 1)
        return view

    def _all_classes(self):
        return [] if self.manager is None else list(self.manager.lay_danh_sach_lop())

    def refresh(self):
        try:
            self._source_classes = self._all_classes()
        except (RuntimeError, ValueError) as error:
            Notification.error(self, str(error))
            self._source_classes = []
        self.class_count_changed.emit(len(self._source_classes))
        if self.manager is not None:
            self.student_count_changed.emit(self.manager.tong_so_sinh_vien())
        self.apply_filters(reset_page=False)
        if self.selected_class_code:
            self.refresh_students()

    def apply_filters(self, *_args, reset_page=True):
        if reset_page:
            self.current_page = 1
        text = self.search_input.text().strip().casefold()
        filtered = [
            item for item in getattr(self, "_source_classes", [])
            if not text
            or text in item.ma_lop.casefold()
            or text in item.ten_lop.casefold()
        ]
        page_count = max(1, math.ceil(len(filtered) / self.PAGE_SIZE))
        self.current_page = min(self.current_page, page_count)
        start = (self.current_page - 1) * self.PAGE_SIZE
        page_items = filtered[start:start + self.PAGE_SIZE]
        self.class_table.set_classes(page_items, start + 1)
        if filtered:
            self.range_label.setText(
                f"Hiển thị {start + 1} – {start + len(page_items)} của {len(filtered)} lớp"
            )
        else:
            self.range_label.setText("Hiển thị 0 lớp")
        self._render_pagination(page_count)

    def open_student_list(self, class_code):
        self.editor_host.close_panel(immediate=True)
        class_item = self.manager.tim_lop(class_code)
        if class_item is None:
            Notification.warning(self, "Không tìm thấy lớp đã chọn.")
            return
        self.selected_class_code = class_code
        self.current_student_page = 1
        self.student_heading.setText(f"Sinh viên lớp {class_code}")
        self.student_class_name.setText(class_item.ten_lop)
        self.content_stack.setCurrentIndex(1)
        self.refresh_students()

    def show_class_list(self):
        self.editor_host.close_panel(immediate=True)
        self.selected_class_code = None
        self.content_stack.setCurrentIndex(0)
        self.refresh()

    def refresh_students(self):
        if not self.selected_class_code or self.manager is None:
            self._source_students = []
        else:
            try:
                self._source_students = list(
                    self.manager.lay_danh_sach_sinh_vien(self.selected_class_code)
                )
            except (RuntimeError, ValueError) as error:
                Notification.error(self, str(error))
                self._source_students = []
        self.apply_student_filter(reset_page=False)

    def apply_student_filter(self, *_args, reset_page=True):
        if reset_page:
            self.current_student_page = 1
        text = self.student_search_input.text().strip().casefold()
        filtered = [
            student for student in getattr(self, "_source_students", [])
            if not text
            or text in student.ma_sv.casefold()
            or text in student.ho_ten.casefold()
            or text in student.so_dt.casefold()
        ]
        page_count = max(1, math.ceil(len(filtered) / self.STUDENT_PAGE_SIZE))
        self.current_student_page = min(self.current_student_page, page_count)
        start = (self.current_student_page - 1) * self.STUDENT_PAGE_SIZE
        page_items = filtered[start:start + self.STUDENT_PAGE_SIZE]
        self.student_table.set_students(page_items, start + 1)
        if filtered:
            self.student_range_label.setText(
                f"Hiển thị {start + 1} – {start + len(page_items)} "
                f"của {len(filtered)} sinh viên"
            )
        else:
            self.student_range_label.setText("Hiển thị 0 sinh viên")
        self._render_student_pagination(page_count)

    def _render_student_pagination(self, page_count):
        while self.student_pagination.count():
            item = self.student_pagination.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        def add_button(text, page, enabled=True, checked=False):
            button = QPushButton(text)
            button.setObjectName("pageButton")
            button.setCheckable(checked)
            button.setChecked(checked and page == self.current_student_page)
            button.setEnabled(enabled)
            button.clicked.connect(
                lambda _checked=False, target=page: self.go_to_student_page(target)
            )
            self.student_pagination.addWidget(button)

        add_button(
            "‹", self.current_student_page - 1,
            self.current_student_page > 1,
        )
        first = max(1, min(self.current_student_page - 3, page_count - 6))
        last = min(page_count, first + 6)
        for page in range(first, last + 1):
            add_button(str(page), page, checked=True)
        add_button(
            "›", self.current_student_page + 1,
            self.current_student_page < page_count,
        )

    def go_to_student_page(self, page):
        self.current_student_page = page
        self.apply_student_filter(reset_page=False)

    def add_class(self):
        def submit(values):
            try:
                self.manager.them_lop(self.class_type(*values))
            except (AttributeError, RuntimeError, ValueError) as error:
                message = str(error)
                return False, message, is_duplicate_error(message)
            self.refresh()
            return True, "Đã thêm lớp.", False

        self.editor_host.open_form(ClassForm(parent=self, on_add=submit))

    def edit_class(self, class_code):
        class_item = self.manager.tim_lop(class_code)
        if class_item is None:
            Notification.warning(self, "Không tìm thấy lớp cần cập nhật.")
            return
        dialog = ClassForm(class_item, self)
        def save():
            try:
                self.manager.cap_nhat_lop(class_code, dialog.values()[1])
            except (RuntimeError, ValueError) as error:
                show_temporary_message(dialog.status_label, str(error), status="error", duration=4000)
                return False
            Notification.success(self, "Đã cập nhật lớp.")
            self.refresh()
            return True

        self.editor_host.open_form(dialog, on_save=save)

    def delete_class(self, class_code):
        if not ConfirmDialog.ask(
            self, "Xóa lớp", f"Bạn có chắc muốn xóa lớp {class_code}?"
        ):
            return
        try:
            self.manager.xoa_lop(class_code)
        except (AttributeError, RuntimeError, ValueError) as error:
            Notification.error(self, str(error))
            return
        Notification.success(self, "Đã xóa lớp.")
        self.refresh()

    def add_student(self):
        if not self.selected_class_code:
            return
        class_code = self.selected_class_code
        def submit(values):
            try:
                self.manager.them_sinh_vien(
                    class_code, self.student_type(*values)
                )
            except (AttributeError, RuntimeError, ValueError) as error:
                message = str(error)
                return False, message, is_duplicate_error(message)
            self.refresh()
            return True, "Đã thêm sinh viên.", False

        self.editor_host.open_form(StudentForm(parent=self, on_add=submit))

    def edit_student(self, student_code):
        student = self.manager.tim_sinh_vien(student_code)
        if student is None:
            Notification.warning(self, "Không tìm thấy sinh viên cần cập nhật.")
            return
        dialog = StudentForm(student, self)
        def save():
            try:
                self.manager.cap_nhat_sinh_vien(
                    student_code, self.student_type(*dialog.values())
                )
            except (RuntimeError, ValueError) as error:
                show_temporary_message(dialog.status_label, str(error), status="error", duration=4000)
                return False
            Notification.success(self, "Đã cập nhật sinh viên.")
            self.refresh()
            return True

        self.editor_host.open_form(dialog, on_save=save)

    def delete_student(self, student_code):
        if not ConfirmDialog.ask(
            self,
            "Xóa sinh viên",
            f"Bạn có chắc muốn xóa sinh viên {student_code}?",
        ):
            return
        try:
            self.manager.xoa_sinh_vien(student_code)
        except (AttributeError, RuntimeError, ValueError) as error:
            Notification.error(self, str(error))
            return
        Notification.success(self, "Đã xóa sinh viên.")
        self.refresh()


__all__ = [
    "ClassForm", "ClassStudentPage", "ClassTable",
    "StudentForm", "StudentTable",
]
