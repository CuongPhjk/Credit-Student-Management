"""Trang đăng ký và hủy đăng ký lớp tín chỉ cho sinh viên."""

from PyQt6.QtCore import QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from frontend.components.confirm_dialog import ConfirmDialog
from frontend.components.input_validation import apply_text_validator
from frontend.components.notification import NotificationBanner, NotificationType
from frontend.pages.dashboard_page import svg_label, svg_pixmap
from frontend.pages.subject_page import SubjectPage


class AvailableClassTable(QTableWidget):
    selection_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        headers = [
            "Chọn", "Mã MH", "Tên môn học", "Nhóm",
            "Đã đăng ký", "Còn trống",
        ]
        super().__init__(0, len(headers), parent)
        self.setHorizontalHeaderLabels(headers)
        self.verticalHeader().hide()
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAlternatingRowColors(True)
        self.setMinimumHeight(245)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for column in (0, 1, 3, 4, 5):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
        widths = {0: 48, 1: 75, 3: 52, 4: 86, 5: 78}
        for column, width in widths.items():
            self.setColumnWidth(column, width)
        self.empty_label = QLabel("Không có lớp tín chỉ phù hợp", self.viewport())
        self.empty_label.setObjectName("subjectEmptyLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.button_group = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.empty_label.setGeometry(self.viewport().rect())

    def set_classes(
        self, classes, subject_names,
    ):
        self.setRowCount(0)
        if self.button_group is not None:
            self.button_group.deleteLater()
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        for credit_class in classes:
            row = self.rowCount()
            self.insertRow(row)
            registered = credit_class.so_sv_dang_ky
            available = max(0, credit_class.so_sv_max - registered)
            values = [
                credit_class.ma_mh,
                subject_names.get(credit_class.ma_mh, credit_class.ma_mh),
                credit_class.nhom,
                registered,
                available,
            ]
            radio_container = QWidget()
            radio_layout = QHBoxLayout(radio_container)
            radio_layout.setContentsMargins(0, 0, 0, 0)
            radio = QRadioButton()
            radio.toggled.connect(
                lambda checked, class_id=credit_class.ma_lop_tc:
                self.selection_changed.emit(class_id) if checked else None
            )
            self.button_group.addButton(radio, credit_class.ma_lop_tc)
            radio_layout.addStretch()
            radio_layout.addWidget(radio)
            radio_layout.addStretch()
            self.setCellWidget(row, 0, radio_container)
            for column, value in enumerate(values, 1):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter
                    | (Qt.AlignmentFlag.AlignLeft if column == 2
                       else Qt.AlignmentFlag.AlignCenter)
                )
                self.setItem(row, column, item)
            self.setRowHeight(row, 38)
        self.empty_label.setVisible(self.rowCount() == 0)
        self.empty_label.raise_()


class RegisteredClassTable(QTableWidget):
    def __init__(self, parent=None):
        headers = [
            "Mã MH", "Tên môn học", "Nhóm"
        ]
        super().__init__(0, len(headers), parent)
        self.setHorizontalHeaderLabels(headers)
        self.verticalHeader().hide()
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMinimumHeight(200)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for column in (0, 2):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
        for column, width in {0: 75, 2: 52}.items():
            self.setColumnWidth(column, width)
        self.empty_label = QLabel("Không có lớp đăng ký còn hiệu lực", self.viewport())
        self.empty_label.setObjectName("subjectEmptyLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.empty_label.setGeometry(self.viewport().rect())

    def set_classes(self, classes, subject_names):
        self.setRowCount(0)
        for credit_class in classes:
            row = self.rowCount()
            self.insertRow(row)
            values = [
                credit_class.ma_mh,
                subject_names.get(credit_class.ma_mh, credit_class.ma_mh),
                credit_class.nhom,
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter
                    | (Qt.AlignmentFlag.AlignLeft if column == 1
                       else Qt.AlignmentFlag.AlignCenter)
                )
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, credit_class.ma_lop_tc)
                self.setItem(row, column, item)
            self.setRowHeight(row, 38)
        self.empty_label.setVisible(self.rowCount() == 0)
        self.empty_label.raise_()

    def selected_class_id(self):
        row = self.currentRow()
        if row < 0 or self.item(row, 0) is None:
            return None
        return self.item(row, 0).data(Qt.ItemDataRole.UserRole)


class RegistrationPage(SubjectPage):
    """Tìm sinh viên, đăng ký và hủy lớp tín chỉ theo học kỳ."""

    registration_changed = pyqtSignal()

    def __init__(
        self,
        registration_manager=None,
        class_student_manager=None,
        credit_class_manager=None,
        subject_manager=None,
        parent=None,
    ):
        self.class_student_manager = class_student_manager
        self.credit_class_manager = credit_class_manager
        self.subject_manager = subject_manager
        self.current_student = None
        self.current_class_code = ""
        self.selected_credit_class_id = None
        super().__init__(registration_manager, None, parent)
        self.select_page("registration", emit_signal=False)

    def _build_content(self):
        content = QWidget()
        content.setObjectName("subjectContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(8)
        controls = QHBoxLayout()
        controls.setSpacing(8)
        controls.addWidget(self._build_student_card(), 3)
        controls.addWidget(self._build_term_card(), 2)
        layout.addLayout(controls)
        layout.addWidget(self.student_info)
        tables = QHBoxLayout()
        tables.setSpacing(8)
        tables.addWidget(self._build_available_card(), 3)
        tables.addWidget(self._build_registered_card(), 2)
        layout.addLayout(tables, 1)
        layout.addWidget(self._build_registration_note())
        layout.addLayout(self._build_actions())
        return content

    def _build_student_card(self):
        card = QFrame()
        card.setObjectName("subjectCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        heading = QLabel("1. Xác nhận sinh viên")
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)
        search_row = QHBoxLayout()
        self.student_input = QLineEdit()
        apply_text_validator(self.student_input)
        self.student_input.setObjectName("subjectSearchInput")
        self.student_input.setProperty("invalid", False)
        self._student_input_error_timer = QTimer(self.student_input)
        self._student_input_error_timer.setSingleShot(True)
        self._student_input_error_timer.timeout.connect(
            lambda: self._set_student_input_invalid(False)
        )
        self.student_input.setPlaceholderText("Nhập mã sinh viên...")
        self.student_input.returnPressed.connect(self.find_student)
        self.student_input.textChanged.connect(self._student_input_changed)
        search_row.addWidget(self.student_input, 1)
        find_button = QPushButton("Tìm sinh viên")
        find_button.setObjectName("primaryButton")
        find_button.setIcon(QIcon(svg_pixmap("search.svg", "#ffffff", 20)))
        find_button.setIconSize(QSize(20, 20))
        find_button.clicked.connect(self.find_student)
        search_row.addWidget(find_button)
        layout.addLayout(search_row)
        self.student_info = QFrame()
        self.student_info.setObjectName("studentInfoCard")
        info_layout = QHBoxLayout(self.student_info)
        info_layout.setContentsMargins(12, 6, 12, 6)
        info_layout.setSpacing(10)
        info_layout.addWidget(svg_label("student.svg", "#087cf0", 34))
        name_column = QVBoxLayout()
        name_column.setSpacing(0)
        self.student_name_label = QLabel("Chưa chọn sinh viên")
        self.student_name_label.setObjectName("studentName")
        self.student_code_label = QLabel("Mã SV: —")
        name_column.addWidget(self.student_name_label)
        name_column.addWidget(self.student_code_label)
        info_layout.addLayout(name_column, 2)
        self.student_class_label = QLabel("Lớp: —")
        self.student_gender_label = QLabel("Phái: —")
        self.student_phone_label = QLabel("SĐT: —")
        info_layout.addWidget(self.student_class_label, 1)
        info_layout.addWidget(self.student_gender_label, 1)
        info_layout.addWidget(self.student_phone_label, 1)
        return card

    def _build_term_card(self):
        card = QFrame()
        card.setObjectName("subjectCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        heading = QLabel("2. Chọn học kỳ")
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)
        row = QHBoxLayout()
        self.year_input = QComboBox()
        self.year_input.setMinimumWidth(165)
        year_column = QVBoxLayout()
        year_label = QLabel("Niên khóa")
        year_label.setObjectName("filterLabel")
        year_column.addWidget(year_label)
        year_column.addWidget(self.year_input)
        self.semester_input = QComboBox()
        self.semester_input.setMinimumWidth(120)
        semester_column = QVBoxLayout()
        semester_label = QLabel("Học kỳ")
        semester_label.setObjectName("filterLabel")
        semester_column.addWidget(semester_label)
        semester_column.addWidget(self.semester_input)
        for semester in range(1, 4):
            self.semester_input.addItem(f"Học kỳ {semester}", semester)
        row.addLayout(year_column)
        row.addLayout(semester_column)
        show_button = QPushButton("Hiển thị lớp đang mở")
        show_button.setObjectName("primaryButton")
        show_button.setIcon(QIcon(svg_pixmap("search.svg", "#ffffff", 20)))
        show_button.clicked.connect(self.load_term)
        row.addWidget(show_button, 0, Qt.AlignmentFlag.AlignBottom)
        layout.addLayout(row)
        return card

    def _build_available_card(self):
        card = QFrame()
        card.setObjectName("subjectCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)
        heading = QLabel("3. Chọn lớp tín chỉ để đăng ký")
        heading.setObjectName("sectionTitle")
        heading.setWordWrap(True)
        layout.addWidget(heading)
        self.available_table = AvailableClassTable()
        self.available_table.selection_changed.connect(self._select_credit_class)
        layout.addWidget(self.available_table, 1)
        footer = QHBoxLayout()
        self.available_count_label = QLabel("Hiển thị 0 lớp đang mở")
        self.available_count_label.setObjectName("rangeLabel")
        footer.addWidget(self.available_count_label)
        footer.addStretch()
        layout.addLayout(footer)
        return card

    def _build_registered_card(self):
        card = QFrame()
        card.setObjectName("subjectCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)
        heading = QLabel("Các lớp đăng ký còn hiệu lực")
        heading.setObjectName("sectionTitle")
        heading.setWordWrap(True)
        layout.addWidget(heading)
        self.registered_table = RegisteredClassTable()
        layout.addWidget(self.registered_table, 1)
        footer = QHBoxLayout()
        self.registered_count_label = QLabel("0 lớp đăng ký còn hiệu lực")
        self.registered_count_label.setObjectName("rangeLabel")
        footer.addWidget(self.registered_count_label)
        footer.addStretch()
        layout.addLayout(footer)
        return card

    def _build_registration_note(self):
        note = QFrame()
        note.setObjectName("infoBanner")
        note_layout = QHBoxLayout(note)
        note_layout.setContentsMargins(10, 7, 10, 7)
        note_layout.addWidget(svg_label("info.svg", "#278df0", 22))
        note_label = QLabel(
            "Không thể đăng ký hai lớp của cùng một môn trong một học kỳ."
        )
        note_label.setWordWrap(True)
        note_layout.addWidget(note_label, 1)
        return note

    def _build_actions(self):
        actions = QHBoxLayout()
        self.page_notice = NotificationBanner()
        self.page_notice.setFixedSize(320, 46)
        notice_policy = self.page_notice.sizePolicy()
        notice_policy.setRetainSizeWhenHidden(True)
        self.page_notice.setSizePolicy(notice_policy)
        self.page_notice.message_label.setWordWrap(True)
        actions.addWidget(self.page_notice)
        actions.addStretch(1)
        self.page_notice_timer = QTimer(self)
        self.page_notice_timer.setSingleShot(True)
        self.page_notice_timer.timeout.connect(self.page_notice.hide)
        clear_button = QPushButton("Hủy chọn")
        clear_button.setObjectName("registrationClearButton")
        clear_button.setFixedSize(200, 46)
        clear_button.clicked.connect(self.clear_selection)
        actions.addWidget(clear_button)
        register_button = QPushButton("Xác nhận đăng ký")
        register_button.setObjectName("successButton")
        register_button.setIcon(QIcon(svg_pixmap("registration.svg", "#ffffff", 20)))
        register_button.setIconSize(QSize(20, 20))
        register_button.setFixedSize(200, 46)
        register_button.clicked.connect(self.register_selected)
        actions.addWidget(register_button)
        return actions

    def _show_page_notice(self, message, kind=NotificationType.ERROR):
        self.page_notice.set_message(message, kind)
        self.page_notice.setToolTip(message)
        self.page_notice_timer.start(3000 if kind == NotificationType.SUCCESS else 4000)

    def _clear_page_notice(self):
        self.page_notice_timer.stop()
        self.page_notice.hide()

    def _apply_style(self):
        super()._apply_style()
        self.setStyleSheet(self.styleSheet() + """
            QFrame#studentInfoCard {
                background: #edf7ff; border: 1px solid #b9ddfb;
                border-radius: 7px;
            }
            QLabel#studentName { color: #0f2b4c; font-size: 17px; font-weight: 700; }
            QPushButton#successButton {
                min-height: 26px; padding: 5px 12px; color: white;
                background: #059669; border: 1px solid #059669;
                border-radius: 6px; font-size: 14px; font-weight: 600;
            }
            QPushButton#successButton:hover { background: #047857; }
            QPushButton#dangerButton {
                min-height: 32px; padding: 7px 15px; color: #dc2626;
                background: white; border: 1px solid #fca5a5;
                border-radius: 6px; font-size: 14px;
            }
            QPushButton#dangerButton:hover { background: #fef2f2; }
            QPushButton#secondaryButton {
                min-height: 32px; min-width: 120px; padding: 7px 18px;
                color: #244f82; background: white;
                border: 1px solid #b9cce3; border-radius: 6px; font-size: 14px;
            }
            QPushButton#secondaryButton:hover { background: #f1f7fc; }
            QPushButton#registrationClearButton {
                padding: 5px 12px; color: #244f82; background: white;
                border: 1px solid #b9cce3; border-radius: 6px; font-size: 14px;
            }
            QPushButton#registrationClearButton:hover { background: #f1f7fc; }
        """)

    def refresh(self):
        self._populate_years()
        if self.current_student is not None:
            info = self.class_student_manager.tim_thong_tin_sinh_vien(
                self.current_student.ma_sv
            )
            self._display_student(info)
        else:
            self.available_table.set_classes([], {})
            self.registered_table.set_classes([], {})

    def _populate_years(self):
        if self.credit_class_manager is None:
            return
        selected = self.year_input.currentData()
        years = []
        for credit_class in self.credit_class_manager.lay_danh_sach_lop_tin_chi():
            if credit_class.nien_khoa not in years:
                years.append(credit_class.nien_khoa)
        years.sort(reverse=True)
        self.year_input.blockSignals(True)
        self.year_input.clear()
        for year in years:
            self.year_input.addItem(year, year)
        index = self.year_input.findData(selected)
        self.year_input.setCurrentIndex(max(0, index))
        self.year_input.blockSignals(False)

    def _set_student_input_invalid(self, invalid):
        if invalid:
            self._student_input_error_timer.start(3000)
        else:
            self._student_input_error_timer.stop()
        self.student_input.setProperty("invalid", invalid)
        self.student_input.style().unpolish(self.student_input)
        self.student_input.style().polish(self.student_input)
        self.student_input.update()

    def _student_input_changed(self, _text):
        self._set_student_input_invalid(False)
        self._clear_page_notice()

    def find_student(self):
        self._clear_page_notice()
        code = self.student_input.text().strip()
        if not code:
            self._set_student_input_invalid(True)
            self._show_page_notice("Vui lòng nhập mã sinh viên")
            self.student_input.setFocus()
            return
        self._set_student_input_invalid(False)
        try:
            info = self.class_student_manager.tim_thong_tin_sinh_vien(code)
        except (AttributeError, RuntimeError, ValueError) as error:
            self._show_page_notice(str(error))
            return
        self._display_student(info)

    def _display_student(self, info):
        if info is None:
            self.current_student = None
            self.current_class_code = ""
            self.selected_credit_class_id = None
            self.student_name_label.setText("Chưa chọn sinh viên")
            self.student_code_label.setText("Mã SV: —")
            self.student_class_label.setText("Lớp: —")
            self.student_gender_label.setText("Phái: —")
            self.student_phone_label.setText("SĐT: —")
            self.available_table.set_classes([], {})
            self.registered_table.set_classes([], {})
            self.available_count_label.setText("Hiển thị 0 lớp đang mở")
            self.registered_count_label.setText("0 lớp đăng ký còn hiệu lực")
            self._show_page_notice("Không tìm thấy sinh viên")
            return
        self.current_student = info["sinh_vien"]
        self.current_class_code = info["ma_lop"]
        self.student_input.setText(self.current_student.ma_sv)
        self.student_name_label.setText(self.current_student.ho_ten)
        self.student_code_label.setText(f"Mã SV: {self.current_student.ma_sv}")
        self.student_class_label.setText(f"Lớp: {self.current_class_code}")
        self.student_gender_label.setText(f"Phái: {self.current_student.phai}")
        self.student_phone_label.setText(f"SĐT: {self.current_student.so_dt}")
        self._load_tables()

    def load_term(self):
        self._clear_page_notice()
        if not self.student_input.text().strip():
            self.student_input.setFocus()
            self._show_page_notice("Vui lòng nhập mã sinh viên")
            return
        if self.current_student is None:
            self._show_page_notice("Vui lòng xác nhận sinh viên trước")
            return
        self._load_tables()

    def _subject_names(self):
        if self.subject_manager is None:
            return {}
        return {
            subject.ma_mh: subject.ten_mh
            for subject in self.subject_manager.lay_danh_sach_mon_hoc()
        }

    def _load_tables(self):
        self._clear_page_notice()
        if self.current_student is None or self.credit_class_manager is None:
            return
        year = self.year_input.currentData()
        semester = self.semester_input.currentData()
        open_classes = [
            item for item in self.credit_class_manager.lay_danh_sach_lop_tin_chi()
            if item.nien_khoa == year and item.hoc_ky == semester and not item.huy_lop
        ]
        registered = [
            item for item in open_classes
            if self.manager.da_dang_ky(item.ma_lop_tc, self.current_student.ma_sv)
        ]
        subject_names = self._subject_names()
        self.available_table.set_classes(
            open_classes, subject_names,
        )
        self.registered_table.set_classes(registered, subject_names)
        self.available_count_label.setText(
            f"Hiển thị {len(open_classes)} lớp đang mở"
        )
        self.registered_count_label.setText(
            f"{len(registered)} lớp đăng ký còn hiệu lực"
        )
        self.selected_credit_class_id = None

    def _select_credit_class(self, class_id):
        self.selected_credit_class_id = class_id
        self._clear_page_notice()

    def clear_selection(self):
        self._clear_page_notice()
        group = self.available_table.button_group
        if group is not None:
            group.setExclusive(False)
            for button in group.buttons():
                button.setChecked(False)
            group.setExclusive(True)
        self.selected_credit_class_id = None

    def register_selected(self):
        self._clear_page_notice()
        if self.current_student is None or self.selected_credit_class_id is None:
            self._show_page_notice("Vui lòng chọn lớp tín chỉ")
            return
        if not ConfirmDialog.ask(
            self,
            "Xác nhận đăng ký",
            f"Đăng ký lớp tín chỉ {self.selected_credit_class_id} cho "
            f"{self.current_student.ma_sv}?",
        ):
            return
        try:
            self.manager.dang_ky(
                self.selected_credit_class_id, self.current_student.ma_sv
            )
        except (AttributeError, RuntimeError, ValueError) as error:
            self._show_page_notice(str(error))
            return
        self._load_tables()
        self._show_page_notice("Đăng ký lớp tín chỉ thành công.", NotificationType.SUCCESS)
        self.registration_changed.emit()



__all__ = ["AvailableClassTable", "RegisteredClassTable", "RegistrationPage"]
