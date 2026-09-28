"""Trang lọc sinh viên đã đăng ký và nhập điểm trực tiếp trên bảng."""

from PyQt6.QtCore import QLocale, Qt
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from frontend.components.confirm_dialog import ConfirmDialog
from frontend.components.notification import Notification
from frontend.components.inline_notice import InlineNotice
from frontend.pages.dashboard_page import svg_label
from frontend.pages.subject_page import SubjectPage


class ScoreTable(QTableWidget):
    """Bảng chỉ cho phép sửa cột điểm bằng ô số giới hạn từ 0 đến 10."""

    def __init__(self, on_score_changed, parent=None):
        super().__init__(0, 5, parent)
        self._on_score_changed = on_score_changed
        self.setHorizontalHeaderLabels(
            ["STT", "MÃ SINH VIÊN", "HỌ", "TÊN", "ĐIỂM"]
        )
        self.verticalHeader().hide()
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setMinimumHeight(360)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(0, 68)
        self.setColumnWidth(1, 165)
        self.setColumnWidth(4, 135)

        self.empty_label = QLabel("Chưa có sinh viên để nhập điểm", self.viewport())
        self.empty_label.setObjectName("subjectEmptyLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.empty_label.setGeometry(self.viewport().rect())

    @staticmethod
    def _readonly_item(value, alignment=Qt.AlignmentFlag.AlignLeft):
        item = QTableWidgetItem(str(value))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | alignment)
        return item

    def set_students(self, students):
        self.setRowCount(0)
        for index, student in enumerate(students, 1):
            row = self.rowCount()
            self.insertRow(row)
            self.setItem(
                row, 0,
                self._readonly_item(index, Qt.AlignmentFlag.AlignCenter),
            )
            self.setItem(
                row, 1,
                self._readonly_item(
                    student["ma_sv"], Qt.AlignmentFlag.AlignCenter
                ),
            )
            self.setItem(row, 2, self._readonly_item(student["ho"]))
            self.setItem(row, 3, self._readonly_item(student["ten"]))

            editor = QLineEdit()
            editor.setObjectName("scoreEditor")
            editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
            validator = QDoubleValidator(0.0, 10.0, 2, editor)
            validator.setNotation(QDoubleValidator.Notation.StandardNotation)
            validator.setLocale(QLocale.c())
            editor.setValidator(validator)
            editor.setMaxLength(5)
            editor.setPlaceholderText("Chưa nhập")
            if student.get("da_co_diem", False):
                editor.setText(f'{float(student["diem"]):g}')
            code = student["ma_sv"]
            editor.textChanged.connect(
                lambda value, student_code=code:
                self._on_score_changed(student_code, value)
            )
            self.setCellWidget(row, 4, editor)
            self.setRowHeight(row, 38)

        self.empty_label.setVisible(self.rowCount() == 0)
        self.empty_label.raise_()

    def score_updates(self, student_codes):
        updates = []
        wanted = set(student_codes)
        for row in range(self.rowCount()):
            code_item = self.item(row, 1)
            editor = self.cellWidget(row, 4)
            if code_item is None or editor is None:
                continue
            code = code_item.text()
            if code in wanted:
                text = editor.text().strip()
                if not text:
                    raise ValueError(
                        f"Điểm của sinh viên {code} không được để trống."
                    )
                try:
                    score = float(text)
                except ValueError as error:
                    raise ValueError(
                        f"Điểm của sinh viên {code} phải là số."
                    ) from error
                if score < 0 or score > 10:
                    raise ValueError(
                        f"Điểm của sinh viên {code} phải từ 0 đến 10."
                    )
                updates.append({"ma_sv": code, "diem": score})
        return updates


class ScorePage(SubjectPage):
    """Nhập hoặc hiệu chỉnh điểm theo niên khóa, học kỳ, môn và nhóm."""

    def __init__(
        self,
        score_manager=None,
        credit_class_manager=None,
        subject_manager=None,
        parent=None,
    ):
        self.credit_class_manager = credit_class_manager
        self.subject_manager = subject_manager
        self._loaded_filter = None
        self._original_scores = {}
        self._dirty_students = set()
        super().__init__(score_manager, None, parent)
        self.select_page("score", emit_signal=False)

    def _build_content(self):
        content = QWidget()
        content.setObjectName("subjectContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(10)

        self.empty_notice = InlineNotice()
        layout.addWidget(self._build_filters())
        layout.addWidget(self.empty_notice)
        layout.addWidget(self._build_table_card(), 1)
        return content

    def _build_filters(self):
        card = QFrame()
        card.setObjectName("subjectCard")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        self.year_input = QComboBox()
        self.semester_input = QComboBox()
        self.subject_input = QComboBox()
        self.group_input = QComboBox()
        self.year_input.setMinimumWidth(175)
        self.semester_input.setMinimumWidth(125)
        self.subject_input.setMinimumWidth(245)
        self.group_input.setMinimumWidth(105)

        layout.addWidget(self._field("Niên khóa", self.year_input))
        layout.addWidget(self._field("Học kỳ", self.semester_input))
        layout.addWidget(self._field("Môn học", self.subject_input), 1)
        layout.addWidget(self._field("Nhóm", self.group_input))
        show_button = QPushButton("Hiển thị danh sách")
        show_button.setObjectName("primaryButton")
        show_button.clicked.connect(self.load_students)
        layout.addWidget(show_button, 0, Qt.AlignmentFlag.AlignBottom)

        self.year_input.currentIndexChanged.connect(self._populate_semesters)
        self.semester_input.currentIndexChanged.connect(self._populate_subjects)
        self.subject_input.currentIndexChanged.connect(self._populate_groups)
        for combo in (self.year_input, self.semester_input,
                      self.subject_input, self.group_input):
            combo.currentIndexChanged.connect(self.empty_notice.dismiss)
        return card

    def _build_table_card(self):
        card = QFrame()
        card.setObjectName("subjectCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        heading = QHBoxLayout()
        title = QLabel("Danh sách sinh viên đã đăng ký")
        title.setObjectName("sectionTitle")
        heading.addWidget(title)
        heading.addStretch()
        self.class_label = QLabel("Chưa chọn lớp tín chỉ")
        self.class_label.setObjectName("rangeLabel")
        heading.addWidget(self.class_label)
        layout.addLayout(heading)

        self.table = ScoreTable(self._score_changed)
        layout.addWidget(self.table, 1)

        notice = QFrame()
        notice.setObjectName("infoBanner")
        notice_layout = QHBoxLayout(notice)
        notice_layout.setContentsMargins(12, 7, 12, 7)
        notice_layout.addWidget(svg_label("info.svg", "#278df0", 24))
        notice_text = QLabel(
            "Điểm hợp lệ từ 0 đến 10. Danh sách chỉ gồm các sinh viên "
            "có đăng ký còn hiệu lực."
        )
        notice_text.setWordWrap(True)
        notice_layout.addWidget(notice_text, 1)
        layout.addWidget(notice)

        footer = QHBoxLayout()
        self.count_label = QLabel("Hiển thị 0 sinh viên")
        self.count_label.setObjectName("rangeLabel")
        footer.addWidget(self.count_label)
        footer.addStretch()
        self.save_button = QPushButton("Lưu điểm")
        self.save_button.setObjectName("successButton")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_scores)
        footer.addWidget(self.save_button)
        layout.addLayout(footer)
        return card

    def _apply_style(self):
        super()._apply_style()
        self.setStyleSheet(self.styleSheet() + """
            QLineEdit#scoreEditor {
                min-height: 20px; margin: 2px 10px; padding: 2px 8px;
                color: #0f2b4c; background: #fff;
                border: 1px solid #9fb7d1; border-radius: 5px;
                font-size: 14px; font-weight: 600;
            }
            QLineEdit#scoreEditor:focus {
                border: 2px solid #087cf0; background: #f5fbff;
            }
            QPushButton#successButton {
                min-height: 32px; padding: 7px 24px; color: white;
                background: #059669; border: 1px solid #059669;
                border-radius: 6px; font-size: 14px; font-weight: 600;
            }
            QPushButton#successButton:hover { background: #047857; }
            QPushButton#successButton:disabled {
                background: #a7c7ba; border-color: #a7c7ba;
            }
        """)

    def _credit_classes(self):
        if self.credit_class_manager is None:
            return []
        try:
            return [
                item
                for item in self.credit_class_manager.lay_danh_sach_lop_tin_chi()
                if not item.huy_lop
            ]
        except (AttributeError, RuntimeError, ValueError):
            return []

    def _subject_names(self):
        if self.subject_manager is None:
            return {}
        try:
            return {
                item.ma_mh: item.ten_mh
                for item in self.subject_manager.lay_danh_sach_mon_hoc()
            }
        except (AttributeError, RuntimeError, ValueError):
            return {}

    @staticmethod
    def _replace_combo(combo, values, selected=None, caption=None):
        combo.blockSignals(True)
        combo.clear()
        for value in values:
            text = caption(value) if caption else str(value)
            combo.addItem(text, value)
        index = combo.findData(selected)
        combo.setCurrentIndex(index if index >= 0 else (0 if values else -1))
        combo.blockSignals(False)

    def _populate_years(self):
        selected = self.year_input.currentData()
        years = sorted(
            {item.nien_khoa for item in self._credit_classes()}, reverse=True
        )
        self._replace_combo(self.year_input, years, selected)
        self._populate_semesters()

    def _populate_semesters(self, _index=None):
        year = self.year_input.currentData()
        selected = self.semester_input.currentData()
        semesters = sorted({
            item.hoc_ky for item in self._credit_classes()
            if item.nien_khoa == year
        })
        self._replace_combo(
            self.semester_input, semesters, selected,
            lambda value: f"Học kỳ {value}",
        )
        self._populate_subjects()

    def _populate_subjects(self, _index=None):
        year = self.year_input.currentData()
        semester = self.semester_input.currentData()
        selected = self.subject_input.currentData()
        codes = sorted({
            item.ma_mh for item in self._credit_classes()
            if item.nien_khoa == year and item.hoc_ky == semester
        })
        names = self._subject_names()
        self._replace_combo(
            self.subject_input, codes, selected,
            lambda code: f"{code} - {names.get(code, code)}",
        )
        self._populate_groups()

    def _populate_groups(self, _index=None):
        year = self.year_input.currentData()
        semester = self.semester_input.currentData()
        subject = self.subject_input.currentData()
        selected = self.group_input.currentData()
        groups = sorted({
            item.nhom for item in self._credit_classes()
            if item.nien_khoa == year
            and item.hoc_ky == semester
            and item.ma_mh == subject
        })
        self._replace_combo(
            self.group_input, groups, selected,
            lambda value: f"Nhóm {value}",
        )

    def _current_filter(self):
        values = (
            self.year_input.currentData(),
            self.semester_input.currentData(),
            self.subject_input.currentData(),
            self.group_input.currentData(),
        )
        return None if any(value is None for value in values) else values

    def refresh(self):
        self._populate_years()
        if self._loaded_filter is not None and not self._dirty_students:
            self._load_filter(self._loaded_filter, notify_empty=False)

    def load_students(self):
        self.empty_notice.dismiss()
        selected_filter = self._current_filter()
        if selected_filter is None:
            self.empty_notice.show_message("Không có dữ liệu")
            return
        if self._dirty_students and not ConfirmDialog.ask(
            self,
            "Bỏ thay đổi chưa lưu",
            "Các điểm vừa sửa chưa được lưu. Bạn có muốn bỏ các thay đổi này?",
        ):
            return
        self._load_filter(selected_filter, notify_empty=True)

    def _load_filter(self, selected_filter, notify_empty):
        self.empty_notice.dismiss()
        if self.manager is None:
            Notification.error(self, "Backend C++ chưa được build hoặc chưa được nạp.")
            return
        year, semester, subject, group = selected_filter
        try:
            students = self.manager.lay_danh_sach_sinh_vien(
                year, semester, subject, group
            )
        except (AttributeError, RuntimeError, ValueError) as error:
            Notification.error(self, str(error))
            return

        self._loaded_filter = selected_filter
        self._original_scores = {
            item["ma_sv"]: (
                bool(item.get("da_co_diem", False)), float(item["diem"])
            )
            for item in students
        }
        self._dirty_students.clear()
        self.table.set_students(students)
        self.save_button.setEnabled(False)
        self.count_label.setText(f"Hiển thị {len(students)} sinh viên")
        self.class_label.setText(
            f"{year} • Học kỳ {semester} • {subject} • Nhóm {group}"
        )
        if notify_empty and not students:
            self.empty_notice.show_message("Không có dữ liệu")

    def _score_changed(self, student_code, value):
        original = self._original_scores.get(student_code)
        if original is None:
            return
        text = str(value).strip()
        try:
            current_score = float(text) if text else None
        except ValueError:
            current_score = None
        had_score, original_score = original
        unchanged = (
            current_score is None and not had_score
        ) or (
            current_score is not None
            and had_score
            and abs(current_score - original_score) <= 0.0001
        )
        if not unchanged:
            self._dirty_students.add(student_code)
        else:
            self._dirty_students.discard(student_code)
        self.save_button.setEnabled(bool(self._dirty_students))

    def save_scores(self):
        if self._loaded_filter is None:
            Notification.warning(self, "Vui lòng hiển thị một lớp tín chỉ trước.")
            return
        if not self._dirty_students:
            Notification.info(self, "Không có điểm nào thay đổi.")
            return
        try:
            updates = self.table.score_updates(self._dirty_students)
        except ValueError as error:
            Notification.warning(self, str(error))
            return
        if len(updates) != len(self._dirty_students):
            Notification.error(self, "Không thể đọc đầy đủ các dòng điểm đã sửa.")
            return

        year, semester, subject, group = self._loaded_filter
        try:
            self.manager.cap_nhat_danh_sach_diem(
                year, semester, subject, group, updates
            )
        except (AttributeError, RuntimeError, TypeError, ValueError) as error:
            Notification.error(self, str(error))
            return

        for update in updates:
            self._original_scores[update["ma_sv"]] = (
                True, float(update["diem"])
            )
        changed_count = len(updates)
        self._dirty_students.clear()
        self.save_button.setEnabled(False)
        Notification.success(self, f"Đã lưu điểm cho {changed_count} sinh viên.")


__all__ = ["ScorePage", "ScoreTable"]
