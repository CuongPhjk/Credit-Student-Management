"""Trang quản lý môn học, sử dụng trực tiếp MonHocManager từ C++."""

import math

from PyQt6.QtCore import (
    QSize, Qt,
    pyqtSignal,
)
from frontend.components.branding import CampusBackground, PtitBrand, SidebarNavButton
from frontend.components.topbar import TopBar

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
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from frontend.components.confirm_dialog import ConfirmDialog
from frontend.components.editor_panel import EditorForm, EditorPanelHost
from frontend.components.input_validation import (
    add_inline_validation,
    apply_text_validator,
    is_duplicate_error,
    show_field_error,
    show_temporary_message,
    text_input_error,
)
from frontend.components.notification import Notification
from frontend.pages.dashboard_page import ICONS, svg_label, svg_pixmap


class SubjectForm(EditorForm):
    """Form dùng chung cho thao tác thêm và cập nhật môn học."""

    def __init__(self, subject=None, parent=None, on_add=None):
        super().__init__(parent)
        self._editing = subject is not None
        self._on_add = on_add
        self.setWindowTitle("Cập nhật môn học" if self._editing else "Thêm môn học")
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
        self.code_input.setMaxLength(10)
        self.code_input.setPlaceholderText("Ví dụ: INT101")
        apply_text_validator(self.code_input)
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(50)
        self.name_input.setPlaceholderText("Nhập tên môn học")
        apply_text_validator(self.name_input)
        self.theory_input = QSpinBox()
        self.theory_input.setRange(1, 20)
        self.theory_input.setValue(3)
        self.practice_input = QSpinBox()
        self.practice_input.setRange(0, 20)
        self.code_error = add_inline_validation(
            form,
            "Mã môn học",
            self.code_input,
        )
        self.name_error = add_inline_validation(
            form,
            "Tên môn học",
            self.name_input,
        )
        form.addRow("Tín chỉ lý thuyết", self.theory_input)
        form.addRow("Tín chỉ thực hành", self.practice_input)
        root.addLayout(form)

        self.status_label = QLabel()
        self.status_label.setObjectName("dialogStatus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.hide()
        root.addWidget(self.status_label)

        if subject is not None:
            self.code_input.setText(subject.ma_mh)
            self.code_input.setReadOnly(True)
            self.name_input.setText(subject.ten_mh)
            self.theory_input.setValue(subject.stc_lt)
            self.practice_input.setValue(subject.stc_th)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Save
        )
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Hủy")
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Lưu")
        buttons.button(QDialogButtonBox.StandardButton.Save).setObjectName("saveButton")
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        self.setStyleSheet("""
            QWidget#subjectDialog { background: white; }
            QLabel#dialogTitle { color: #0f2b4c; font-size: 18px; font-weight: 700; }
            QLineEdit, QSpinBox { min-height: 28px; }
            QLineEdit[invalid="true"] { border: 1px solid #dc2626; }
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
            show_field_error(
                self.code_input, self.code_error, "Vui lòng nhập mã môn học."
            )
            has_error = True
        elif error := text_input_error(code):
            show_field_error(self.code_input, self.code_error, f"Mã môn học {error}.")
            has_error = True
        if not name.strip():
            show_field_error(
                self.name_input, self.name_error, "Vui lòng nhập tên môn học."
            )
            has_error = True
        elif error := text_input_error(name):
            show_field_error(self.name_input, self.name_error, f"Tên môn học {error}.")
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
        self.theory_input.setValue(3)
        self.practice_input.setValue(0)
        self.code_input.setFocus()

    def values(self):
        return (
            self.code_input.text(),
            self.name_input.text(),
            self.theory_input.value(),
            self.practice_input.value(),
        )


class SubjectTable(QTableWidget):
    edit_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        headers = [
            "STT", "Mã môn học", "Tên môn học", "Tín chỉ lý thuyết",
            "Tín chỉ thực hành", "Tổng tín chỉ", "Thao tác",
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
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(0, 65)
        self.setColumnWidth(1, 125)
        self.setColumnWidth(6, 135)

        self.empty_label = QLabel("Chưa có dữ liệu", self.viewport())
        self.empty_label.setObjectName("subjectEmptyLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._sync_empty_state()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.empty_label.setGeometry(self.viewport().rect())

    def set_subjects(self, subjects, first_number=1):
        self.setRowCount(0)
        for offset, subject in enumerate(subjects):
            row = self.rowCount()
            self.insertRow(row)
            values = [
                first_number + offset,
                subject.ma_mh,
                subject.ten_mh,
                subject.stc_lt,
                subject.stc_th,
                subject.tong_tin_chi,
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                alignment = Qt.AlignmentFlag.AlignVCenter
                if column == 2:
                    alignment |= Qt.AlignmentFlag.AlignLeft
                else:
                    alignment |= Qt.AlignmentFlag.AlignCenter
                item.setTextAlignment(alignment)
                self.setItem(row, column, item)
            self.setCellWidget(row, 6, self._action_widget(subject.ma_mh))
            self.setRowHeight(row, 38)
        self._sync_empty_state()

    def _action_widget(self, code):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(9)
        edit_button = QPushButton()
        edit_button.setObjectName("tableActionButton")
        edit_button.setToolTip("Cập nhật môn học")
        edit_button.setIcon(QIcon(svg_pixmap("edit.svg", "#27466f", 19)))
        delete_button = QPushButton()
        delete_button.setObjectName("tableActionButton")
        delete_button.setToolTip("Xóa môn học")
        delete_button.setIcon(QIcon(svg_pixmap("delete.svg", "#ef233c", 19)))
        for button in (edit_button, delete_button):
            button.setFixedSize(28, 28)
            button.setIconSize(QSize(19, 19))
            button.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_button.clicked.connect(lambda _checked=False: self.edit_requested.emit(code))
        delete_button.clicked.connect(lambda _checked=False: self.delete_requested.emit(code))
        layout.addStretch()
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        layout.addStretch()
        return widget

    def _sync_empty_state(self):
        self.empty_label.setVisible(self.rowCount() == 0)
        self.empty_label.raise_()


class SubjectPage(QWidget):
    """Màn hình CRUD môn học với tìm kiếm, bộ lọc và phân trang."""

    navigation_requested = pyqtSignal(str)
    subject_count_changed = pyqtSignal(int)
    PAGE_SIZE = 12

    def __init__(self, manager=None, subject_type=None, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.subject_type = subject_type
        self.current_page = 1
        self.filtered_subjects = []
        self.setObjectName("subjectPage")
        self.setMinimumSize(1050, 680)
        self._build_ui()
        self._apply_style()
        self.refresh()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_sidebar())

        right = QWidget()
        right.setObjectName("subjectRight")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self._build_topbar())
        scroll = QScrollArea()
        scroll.setObjectName("subjectScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(self._build_content())
        self.editor_host = EditorPanelHost(scroll)
        right_layout.addWidget(self.editor_host, 1)
        root.addWidget(right, 1)

    def _build_sidebar(self):
        sidebar = CampusBackground()
        sidebar.setObjectName("subjectSidebar")
        sidebar.setFixedWidth(210)
        self.sidebar = sidebar
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 8, 10, 16)
        layout.setSpacing(7)

        brand = PtitBrand()
        self.brand_subtitle = brand.subtitle
        layout.addWidget(brand)

        items = [
            ("dashboard", "home.svg", "Trang chủ"),
            ("student", "class.svg", "Lớp & Sinh viên"),
            ("subject", "subject.svg", "Môn học"),
            ("credit_class", "credit_class.svg", "Lớp tín chỉ"),
            ("registration", "registration.svg", "Đăng ký học"),
            ("score", "score.svg", "Nhập điểm"),
        ]
        self.nav_buttons = {}
        for key, icon_name, caption in items:
            button = SidebarNavButton(caption)
            button.setObjectName("subjectNavButton")
            button.setCheckable(True)
            button.setIcon(QIcon(svg_pixmap(icon_name, "#ffffff", 25)))
            button.setIconSize(QSize(25, 25))
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda _checked=False, page=key: self.select_page(page)
            )
            self.nav_buttons[key] = button
            layout.addWidget(button)
        layout.addStretch()
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet("background: #6690b1; border: none;")
        layout.addWidget(line)
        self.sidebar_version = QLabel("Phiên bản 1.0.0\nNăm học 2025 - 2026")
        self.sidebar_version.setObjectName("sidebarVersion")
        layout.addWidget(self.sidebar_version)
        self.select_page("subject", emit_signal=False)
        return sidebar

    def _build_topbar(self):
        return TopBar()

    def _build_content(self):
        content = QWidget()
        content.setObjectName("subjectContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(self._build_filters())
        layout.addWidget(self._build_table_card(), 1)
        return content

    def _field(self, caption, widget):
        container = QWidget()
        field_layout = QVBoxLayout(container)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(5)
        label = QLabel(caption)
        label.setObjectName("filterLabel")
        field_layout.addWidget(label)
        field_layout.addWidget(widget)
        return container

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
        self.search_input.setPlaceholderText("Tìm theo mã hoặc tên môn học...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.returnPressed.connect(self.submit_search)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        search_field = self._field("Tìm kiếm", self.search_input)
        search_field.setMinimumWidth(280)
        layout.addWidget(search_field, 2)
        self.theory_filter = QComboBox()
        self.practice_filter = QComboBox()
        for combo in (self.theory_filter, self.practice_filter):
            combo.addItem("Tất cả", None)
            for value in range(0, 11):
                combo.addItem(str(value), value)
            combo.currentIndexChanged.connect(self.apply_filters)
        layout.addWidget(self._field("Tín chỉ LT", self.theory_filter), 1)
        layout.addWidget(self._field("Tín chỉ TH", self.practice_filter), 1)
        search_button = QPushButton("Tìm kiếm")
        search_button.setObjectName("primaryButton")
        search_button.setIcon(QIcon(svg_pixmap("search.svg", "#ffffff", 20)))
        search_button.setIconSize(QSize(20, 20))
        search_button.clicked.connect(self.submit_search)
        layout.addWidget(search_button, 0, Qt.AlignmentFlag.AlignBottom)
        divider = QFrame()
        divider.setFixedSize(1, 42)
        divider.setStyleSheet("background: #d8e2ef; border: none;")
        layout.addWidget(divider)
        add_button = QPushButton("Thêm môn học")
        add_button.setObjectName("primaryButton")
        add_button.setIcon(QIcon(svg_pixmap("plus.svg", "#ffffff", 21)))
        add_button.setIconSize(QSize(21, 21))
        add_button.clicked.connect(self.add_subject)
        layout.addWidget(add_button, 0, Qt.AlignmentFlag.AlignBottom)
        return card

    def _build_table_card(self):
        card = QFrame()
        card.setObjectName("subjectCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        heading = QLabel("Danh sách môn học")
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)
        self.table = SubjectTable()
        self.table.edit_requested.connect(self.edit_subject)
        self.table.delete_requested.connect(self.delete_subject)
        layout.addWidget(self.table, 1)
        notice = QFrame()
        notice.setObjectName("infoBanner")
        notice_layout = QHBoxLayout(notice)
        notice_layout.setContentsMargins(12, 7, 12, 7)
        notice_layout.addWidget(svg_label("info.svg", "#278df0", 24))
        notice_layout.addWidget(QLabel(
            "<b>Lưu ý:</b> Không thể xóa môn học đã được sử dụng trong một lớp "
            "tín chỉ. Vui lòng kiểm tra trước khi thực hiện."
        ), 1)
        layout.addWidget(notice)
        footer = QHBoxLayout()
        self.range_label = QLabel("Hiển thị 0 môn học")
        self.range_label.setObjectName("rangeLabel")
        footer.addWidget(self.range_label)
        footer.addStretch()
        self.pagination = QHBoxLayout()
        self.pagination.setSpacing(5)
        footer.addLayout(self.pagination)
        layout.addLayout(footer)
        return card

    def _apply_style(self):
        style = """
            QWidget#subjectPage, QWidget#subjectRight, QWidget#subjectContent {
                background: #f3f9fd; color: #0f2b4c; font-family: "Segoe UI";
            }
            QScrollArea#subjectScroll { background: transparent; border: none; }
            QScrollArea#subjectScroll > QWidget > QWidget { background: #f3f9fd; }
            QFrame#subjectSidebar { background: transparent; border: none; }
            QLabel#brandSubtitle { color: #7dd3fc; font-size: 12px; font-weight: 600; }
            QLabel#sidebarVersion { color: white; font-size: 12px; line-height: 1.5; }
            QFrame#subjectTopbar { background: white; border: none; border-bottom: 1px solid #e2e8f0; }
            QLabel#topbarTitle { color: #0f2b4c; font-size: 17px; font-weight: 700; }
            QFrame#subjectCard { background: white; border: 1px solid #d8e2ef; border-radius: 9px; }
            QLabel#filterLabel { color: #0f2b4c; font-size: 14px; }
            QLineEdit, QComboBox { min-height: 24px; font-size: 13px; }
            QLineEdit#subjectSearchInput[invalid="true"] {
                border: 2px solid #ef233c; border-radius: 5px;
                background: #fff5f5;
            }
            QPushButton#primaryButton {
                min-height: 26px; padding: 5px 12px; color: white; background: #087cf0;
                border: 1px solid #087cf0; border-radius: 6px; font-size: 14px;
            }
            QPushButton#primaryButton:hover { background: #076bd0; }
            QLabel#sectionTitle { color: #0f2b4c; font-size: 17px; font-weight: 700; }
            QTableWidget { border: 1px solid #d8e2ef; gridline-color: #d8e2ef; color: #0f2b4c; }
            QTableWidget::item { padding: 4px 7px; }
            QHeaderView::section {
                background: #eef4f9; color: #0f2b4c; font-size: 13px; font-weight: 700;
                padding: 7px 6px; border: none; border-right: 1px solid #d8e2ef;
                border-bottom: 1px solid #d8e2ef;
            }
            QLabel#subjectEmptyLabel { color: #94a3b8; font-size: 15px; background: white; }
            QPushButton#tableActionButton { background: transparent; border: none; padding: 5px; }
            QPushButton#tableActionButton:hover { background: #edf6ff; }
            QFrame#infoBanner { background: #edf7ff; border: 1px solid #abd8ff; border-radius: 6px; }
            QFrame#infoBanner QLabel { color: #076bd0; font-size: 12px; }
            QLabel#rangeLabel { color: #244f82; font-size: 13px; }
            QPushButton#pageButton {
                min-width: 29px; min-height: 25px; padding: 2px; color: #244f82;
                background: white; border: 1px solid #d8e2ef; border-radius: 5px;
            }
            QPushButton#pageButton:checked { color: white; background: #087cf0; border-color: #087cf0; }
            QPushButton#pageButton:disabled { color: #a4b2c3; background: #f8fafc; }
        """
        arrow_path = (ICONS / "chevron_down.svg").as_posix()
        style += f"""
            QComboBox {{ padding-right: 28px; }}
            QComboBox::drop-down {{
                subcontrol-origin: padding; subcontrol-position: top right;
                width: 27px; border: none;
            }}
            QComboBox::down-arrow {{
                image: url("{arrow_path}"); width: 20px; height: 14px;
            }}
        """
        self.setStyleSheet(style)

    def select_page(self, page_name, emit_signal=True):
        for key, button in self.nav_buttons.items():
            button.setChecked(key == page_name)
        if emit_signal:
            self.navigation_requested.emit(page_name)

    def _all_subjects(self):
        if self.manager is None:
            return []
        return list(self.manager.lay_danh_sach_mon_hoc())

    def refresh(self):
        try:
            subjects = self._all_subjects()
        except (RuntimeError, ValueError) as error:
            Notification.error(self, str(error))
            subjects = []
        self.subject_count_changed.emit(len(subjects))
        self._source_subjects = subjects
        self.apply_filters(reset_page=False)

    def _set_search_invalid(self, invalid):
        self.search_input.setProperty("invalid", invalid)
        self.search_input.style().unpolish(self.search_input)
        self.search_input.style().polish(self.search_input)
        self.search_input.update()

    def _on_search_text_changed(self, _text):
        if self.search_input.property("invalid"):
            self._set_search_invalid(False)
        self.apply_filters()

    def submit_search(self):
        if not self.search_input.text().strip():
            self._set_search_invalid(True)
            self.search_input.setFocus()
            return
        self._set_search_invalid(False)
        self.apply_filters()

    def apply_filters(self, *_args, reset_page=True):
        if reset_page:
            self.current_page = 1
        text = self.search_input.text().strip().casefold()
        theory = self.theory_filter.currentData()
        practice = self.practice_filter.currentData()
        self.filtered_subjects = [
            subject for subject in getattr(self, "_source_subjects", [])
            if (not text or text in subject.ma_mh.casefold() or text in subject.ten_mh.casefold())
            and (theory is None or subject.stc_lt == theory)
            and (practice is None or subject.stc_th == practice)
        ]
        page_count = max(1, math.ceil(len(self.filtered_subjects) / self.PAGE_SIZE))
        self.current_page = min(self.current_page, page_count)
        start = (self.current_page - 1) * self.PAGE_SIZE
        page_items = self.filtered_subjects[start:start + self.PAGE_SIZE]
        self.table.set_subjects(page_items, start + 1)
        if self.filtered_subjects:
            self.range_label.setText(
                f"Hiển thị {start + 1} – {start + len(page_items)} "
                f"của {len(self.filtered_subjects)} môn học"
            )
        else:
            self.range_label.setText("Hiển thị 0 môn học")
        self._render_pagination(page_count)

    def _render_pagination(self, page_count):
        while self.pagination.count():
            item = self.pagination.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        def add_button(text, page, enabled=True, checked=False):
            button = QPushButton(text)
            button.setObjectName("pageButton")
            button.setCheckable(checked)
            button.setChecked(checked and page == self.current_page)
            button.setEnabled(enabled)
            button.clicked.connect(lambda _checked=False: self.go_to_page(page))
            self.pagination.addWidget(button)

        add_button("‹", self.current_page - 1, self.current_page > 1)
        first = max(1, min(self.current_page - 3, page_count - 6))
        last = min(page_count, first + 6)
        for page in range(first, last + 1):
            add_button(str(page), page, checked=True)
        add_button("›", self.current_page + 1, self.current_page < page_count)

    def go_to_page(self, page):
        self.current_page = page
        self.apply_filters(reset_page=False)

    def _new_subject(self, values):
        if self.subject_type is None:
            raise RuntimeError("Backend C++ chưa được build hoặc chưa được nạp.")
        return self.subject_type(*values)

    def add_subject(self):
        def submit(values):
            try:
                self.manager.them_mon_hoc(self._new_subject(values))
            except (AttributeError, RuntimeError, ValueError) as error:
                message = str(error)
                return False, message, is_duplicate_error(message)
            self.refresh()
            return True, "Đã thêm môn học.", False

        self.editor_host.open_form(SubjectForm(parent=self, on_add=submit))

    def edit_subject(self, code):
        try:
            subject = self.manager.tim_mon_hoc(code)
        except (AttributeError, RuntimeError, ValueError) as error:
            Notification.error(self, str(error))
            return
        if subject is None:
            Notification.warning(self, "Không tìm thấy môn học cần cập nhật.")
            return
        dialog = SubjectForm(subject, self)
        def save():
            try:
                self.manager.cap_nhat_mon_hoc(code, self._new_subject(dialog.values()))
            except (RuntimeError, ValueError) as error:
                show_temporary_message(dialog.status_label, str(error), status="error", duration=4000)
                return False
            Notification.success(self, "Đã cập nhật môn học.")
            self.refresh()
            return True

        self.editor_host.open_form(dialog, on_save=save)

    def delete_subject(self, code):
        if not ConfirmDialog.ask(
            self,
            "Xóa môn học",
            f"Bạn có chắc muốn xóa môn học {code}?",
        ):
            return
        try:
            self.manager.xoa_mon_hoc(code)
        except (AttributeError, RuntimeError, ValueError) as error:
            Notification.error(self, str(error))
            return
        Notification.success(self, "Đã xóa môn học.")
        self.refresh()


__all__ = ["SubjectForm", "SubjectPage", "SubjectTable"]
