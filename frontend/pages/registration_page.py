"""Trang đăng ký và hủy đăng ký lớp tín chỉ cho sinh viên."""

from PyQt6.QtCore import QSize, Qt, pyqtSignal
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
from frontend.components.inline_notice import InlineNotice
from frontend.components.notification import Notification
from frontend.pages.dashboard_page import status_badge, svg_label, svg_pixmap
from frontend.pages.subject_page import SubjectPage


class AvailableClassTable(QTableWidget):
    selection_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        headers = [
            "Chọn", "Mã MH", "Tên môn học", "Nhóm",
            "Đã đăng ký", "Còn trống", "Trạng thái",
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
        for column in (0, 1, 3, 4, 5, 6):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
        widths = {0: 48, 1: 75, 3: 52, 4: 86, 5: 78, 6: 108}
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
        self, classes, subject_names, registered_subjects,
        registered_class_ids=None,
    ):
        registered_class_ids = registered_class_ids or set()
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
            selectable = available > 0 and credit_class.ma_mh not in registered_subjects
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
            radio.setEnabled(selectable)
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
            if available == 0:
                status, tone = "Đã đầy", "red"
            elif available <= max(3, round(credit_class.so_sv_max * 0.2)):
                status, tone = "Sắp đầy", "yellow"
            else:
                status, tone = "Còn chỗ", "green"
            if credit_class.ma_lop_tc in registered_class_ids:
                status, tone = "Đã đăng ký", "blue"
            elif credit_class.ma_mh in registered_subjects:
                status, tone = "Trùng môn", "yellow"
            self.setCellWidget(row, 6, status_badge(status, tone))
            self.setRowHeight(row, 38)
        self.empty_label.setVisible(self.rowCount() == 0)
        self.empty_label.raise_()


class RegisteredClassTable(QTableWidget):
    def __init__(self, parent=None):
        headers = [
            "Mã MH", "Tên môn học", "Nhóm", "Trạng thái"
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
        for column in (0, 2, 3):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
        for column, width in {0: 75, 2: 52, 3: 108}.items():
            self.setColumnWidth(column, width)
        self.empty_label = QLabel("Sinh viên chưa đăng ký lớp nào", self.viewport())
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
            self.setCellWidget(row, 3, status_badge("Đã đăng ký", "green"))
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
        self.student_notice = InlineNotice()
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
        self.semester_input = QComboBox()
        self.semester_input.setMinimumWidth(120)
        for semester in range(1, 4):
            self.semester_input.addItem(f"Học kỳ {semester}", semester)
        row.addWidget(self.year_input)
        row.addWidget(self.semester_input)
        show_button = QPushButton("Hiển thị lớp đang mở")
        show_button.setObjectName("primaryButton")
        show_button.setIcon(QIcon(svg_pixmap("search.svg", "#ffffff", 20)))
        show_button.clicked.connect(self.load_term)
        row.addWidget(show_button)
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
        heading = QLabel("Các lớp đã đăng ký trong học kỳ")
        heading.setObjectName("sectionTitle")
        heading.setWordWrap(True)
        layout.addWidget(heading)
        self.registered_table = RegisteredClassTable()
        layout.addWidget(self.registered_table, 1)
        footer = QHBoxLayout()
        self.registered_count_label = QLabel("0 lớp đã đăng ký")
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
        actions.addWidget(self.student_notice, 1)
        self.registration_notice = InlineNotice()
        actions.addWidget(self.registration_notice, 1)
        clear_button = QPushButton("Hủy chọn")
        clear_button.setObjectName("secondaryButton")
        clear_button.clicked.connect(self.clear_selection)
        actions.addWidget(clear_button)
        register_button = QPushButton("Xác nhận đăng ký")
        register_button.setObjectName("successButton")
        register_button.setIcon(QIcon(svg_pixmap("registration.svg", "#ffffff", 20)))
        register_button.setIconSize(QSize(20, 20))
        register_button.clicked.connect(self.register_selected)
        actions.addWidget(register_button)
        return actions

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
        """)

    def refresh(self):
        self._populate_years()
        if self.current_student is not None:
            self._load_tables()
        else:
            self.available_table.set_classes([], {}, set(), set())
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
            self.year_input.addItem(f"Niên khóa {year}", year)
        index = self.year_input.findData(selected)
        self.year_input.setCurrentIndex(max(0, index))
        self.year_input.blockSignals(False)

    def _set_student_input_invalid(self, invalid):
        self.student_input.setProperty("invalid", invalid)
        self.student_input.style().unpolish(self.student_input)
        self.student_input.style().polish(self.student_input)
        self.student_input.update()

    def _student_input_changed(self, _text):
        self._set_student_input_invalid(False)
        self.student_notice.dismiss()
        self.registration_notice.dismiss()

    def find_student(self):
        self.student_notice.dismiss()
        code = self.student_input.text().strip()
        if not code:
            self._set_student_input_invalid(True)
            self.student_input.setFocus()
            return
        self._set_student_input_invalid(False)
        try:
            info = self.class_student_manager.tim_thong_tin_sinh_vien(code)
        except (AttributeError, RuntimeError, ValueError) as error:
            Notification.error(self, str(error))
            return
        if info is None:
            self.current_student = None
            self.current_class_code = ""
            self.selected_credit_class_id = None
            self.student_name_label.setText("Chưa chọn sinh viên")
            self.student_code_label.setText("Mã SV: —")
            self.student_class_label.setText("Lớp: —")
            self.student_gender_label.setText("Phái: —")
            self.student_phone_label.setText("SĐT: —")
            self.available_table.set_classes([], {}, set(), set())
            self.registered_table.set_classes([], {})
            self.available_count_label.setText("Hiển thị 0 lớp đang mở")
            self.registered_count_label.setText("0 lớp đã đăng ký")
            self.student_notice.show_message("Không tìm thấy sinh viên")
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
        self.student_notice.dismiss()
        if not self.student_input.text().strip():
            self.student_input.setFocus()
            self.student_notice.show_message("Vui lòng nhập mã sinh viên")
            return
        if self.current_student is None:
            self.student_notice.show_message("Vui lòng xác nhận sinh viên trước")
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
        self.registration_notice.dismiss()
        if self.current_student is None or self.credit_class_manager is None:
            return
        year = self.year_input.currentData()
        semester = self.semester_input.currentData()
        all_classes = [
            item for item in self.credit_class_manager.lay_danh_sach_lop_tin_chi()
            if item.nien_khoa == year and item.hoc_ky == semester
        ]
        registered = [
            item for item in all_classes
            if self.manager.da_dang_ky(item.ma_lop_tc, self.current_student.ma_sv)
        ]
        open_classes = [item for item in all_classes if not item.huy_lop]
        registered_subjects = {item.ma_mh for item in registered}
        registered_class_ids = {item.ma_lop_tc for item in registered}
        subject_names = self._subject_names()
        self.available_table.set_classes(
            open_classes, subject_names, registered_subjects,
            registered_class_ids,
        )
        self.registered_table.set_classes(registered, subject_names)
        self.available_count_label.setText(
            f"Hiển thị {len(open_classes)} lớp đang mở"
        )
        self.registered_count_label.setText(
            f"{len(registered)} lớp đã đăng ký"
        )
        self.selected_credit_class_id = None

    def _select_credit_class(self, class_id):
        self.selected_credit_class_id = class_id
        self.registration_notice.dismiss()

    def clear_selection(self):
        self.registration_notice.dismiss()
        group = self.available_table.button_group
        if group is not None:
            group.setExclusive(False)
            for button in group.buttons():
                button.setChecked(False)
            group.setExclusive(True)
        self.selected_credit_class_id = None

    def register_selected(self):
        self.registration_notice.dismiss()
        if self.current_student is None or self.selected_credit_class_id is None:
            self.registration_notice.show_message("Vui lòng chọn lớp tín chỉ")
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
            Notification.error(self, str(error))
            return
        Notification.success(self, "Đăng ký lớp tín chỉ thành công.")
        self._load_tables()

    def cancel_registration(self):
        if self.current_student is None:
            Notification.warning(self, "Vui lòng xác nhận sinh viên trước.")
            return
        class_id = self.registered_table.selected_class_id()
        if class_id is None:
            Notification.warning(self, "Vui lòng chọn lớp cần hủy đăng ký.")
            return
        if not ConfirmDialog.ask(
            self,
            "Hủy đăng ký",
            f"Bạn có chắc muốn hủy đăng ký lớp tín chỉ {class_id}?",
        ):
            return
        try:
            self.manager.huy_dang_ky(class_id, self.current_student.ma_sv)
        except (AttributeError, RuntimeError, ValueError) as error:
            Notification.error(self, str(error))
            return
        Notification.success(self, "Đã hủy đăng ký lớp tín chỉ.")
        self._load_tables()


__all__ = ["AvailableClassTable", "RegisteredClassTable", "RegistrationPage"]
