"""Cửa sổ chính của ứng dụng quản lý tín chỉ."""

from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget

from bridge import (
    AppData,
    DangKyManager,
    DiemManager,
    Lop,
    LopSinhVienManager,
    LopTinChi,
    LopTinChiManager,
    MonHoc,
    MonHocManager,
    SinhVien,
    backend_available,
)
from frontend.pages import (
    ClassStudentPage,
    CreditClassPage,
    DashboardPage,
    RegistrationPage,
    ScorePage,
    SubjectPage,
)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hệ thống quản lý tín chỉ sinh viên")
        self.setMinimumSize(1050, 680)
        self.resize(1536, 900)

        self.app_data = None
        self.subject_manager = None
        self.credit_class_manager = None
        self.class_student_manager = None
        self.registration_manager = None
        self.score_manager = None
        load_error = None
        if backend_available():
            self.app_data = AppData()
            self.subject_manager = MonHocManager(self.app_data)
            self.credit_class_manager = LopTinChiManager(self.app_data)
            self.class_student_manager = LopSinhVienManager(self.app_data)
            self.registration_manager = DangKyManager(self.app_data)
            self.score_manager = DiemManager(self.app_data)
            data_dir = Path(__file__).resolve().parents[1] / "backend" / "data"
            try:
                self.subject_manager.doc_danh_sach_mon_hoc(
                    str(data_dir / "monhoc.txt")
                )
                self.class_student_manager.doc_danh_sach_lop_sinh_vien(
                    str(data_dir / "lopsinhvien.txt")
                )
                self.credit_class_manager.doc_danh_sach_lop_tin_chi(
                    str(data_dir / "loptinchi.txt")
                )
            except (RuntimeError, ValueError) as error:
                load_error = str(error)

        self.dashboard_page = DashboardPage()
        self.subject_page = SubjectPage(self.subject_manager, MonHoc)
        self.credit_class_page = CreditClassPage(
            self.credit_class_manager,
            LopTinChi,
            self.subject_manager,
        )
        self.class_student_page = ClassStudentPage(
            self.class_student_manager,
            Lop,
            SinhVien,
        )
        self.registration_page = RegistrationPage(
            self.registration_manager,
            self.class_student_manager,
            self.credit_class_manager,
            self.subject_manager,
        )
        self.score_page = ScorePage(
            self.score_manager,
            self.credit_class_manager,
            self.subject_manager,
        )
        self.pages = QStackedWidget()
        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.subject_page)
        self.pages.addWidget(self.credit_class_page)
        self.pages.addWidget(self.class_student_page)
        self.pages.addWidget(self.registration_page)
        self.pages.addWidget(self.score_page)
        self.setCentralWidget(self.pages)

        self.dashboard_page.navigation_requested.connect(self.show_page)
        self.subject_page.navigation_requested.connect(self.show_page)
        self.credit_class_page.navigation_requested.connect(self.show_page)
        self.class_student_page.navigation_requested.connect(self.show_page)
        self.registration_page.navigation_requested.connect(self.show_page)
        self.score_page.navigation_requested.connect(self.show_page)
        self.subject_page.subject_count_changed.connect(self._update_subject_count)
        self.credit_class_page.credit_class_count_changed.connect(
            self._update_credit_class_count
        )
        self.class_student_page.class_count_changed.connect(
            self._update_class_count
        )
        self.class_student_page.student_count_changed.connect(
            self._update_student_count
        )
        if self.subject_manager is not None:
            self._update_subject_count(self.subject_manager.tong_so_mon_hoc())
            self._update_credit_class_count(
                self.credit_class_manager.tong_so_lop_tin_chi()
            )
            self._update_class_count(self.class_student_manager.tong_so_lop())
            self._update_student_count(
                self.class_student_manager.tong_so_sinh_vien()
            )
        self.show_page("dashboard")

        logo = self.dashboard_page.windowIcon()
        if not logo.isNull():
            self.setWindowIcon(QIcon(logo))

        if not backend_available():
            QMessageBox.warning(
                self,
                "Backend chưa sẵn sàng",
                "Không thể nạp extension C++. Hãy build project bằng CMake trước "
                "khi sử dụng các chức năng quản lý dữ liệu.",
            )
        elif load_error:
            QMessageBox.warning(
                self,
                "Không thể đọc dữ liệu",
                load_error,
            )

    def show_page(self, page_name):
        if page_name == "open_credit_class":
            self.show_page("credit_class")
            QTimer.singleShot(0, self.credit_class_page.add_credit_class)
            return
        if page_name == "dashboard":
            self._refresh_dashboard_credit_classes()
            self.pages.setCurrentWidget(self.dashboard_page)
            self.dashboard_page.select_page("dashboard", emit_signal=False)
            return
        if page_name == "subject":
            self.subject_page.refresh()
            self.pages.setCurrentWidget(self.subject_page)
            self.subject_page.select_page("subject", emit_signal=False)
            return
        if page_name == "credit_class":
            self.credit_class_page.refresh()
            self.pages.setCurrentWidget(self.credit_class_page)
            self.credit_class_page.select_page(
                "credit_class", emit_signal=False
            )
            return
        if page_name == "student":
            self.class_student_page.refresh()
            self.pages.setCurrentWidget(self.class_student_page)
            self.class_student_page.select_page("student", emit_signal=False)
            return
        if page_name == "registration":
            self.registration_page.refresh()
            self.pages.setCurrentWidget(self.registration_page)
            self.registration_page.select_page(
                "registration", emit_signal=False
            )
            return
        if page_name == "score":
            self.score_page.refresh()
            self.pages.setCurrentWidget(self.score_page)
            self.score_page.select_page("score", emit_signal=False)
            return

    def _refresh_dashboard_credit_classes(self):
        if self.credit_class_manager is None:
            self.dashboard_page.set_attention_rows()
            return

        try:
            credit_classes = list(
                self.credit_class_manager.lay_danh_sach_lop_tin_chi()
            )
        except (AttributeError, RuntimeError, ValueError):
            self.dashboard_page.set_attention_rows()
            return

        rows = []
        for credit_class in credit_classes:
            status = credit_class.trang_thai
            if status == "Đang mở":
                continue
            rows.append((
                credit_class.ma_lop_tc,
                credit_class.ma_mh,
                credit_class.nhom,
                credit_class.so_sv_dang_ky,
                credit_class.so_sv_min,
                status,
            ))

        self.dashboard_page.set_attention_rows(rows)

    def _update_subject_count(self, count):
        self.dashboard_page.stat_cards["subjects"].set_value(count)

    def _update_credit_class_count(self, count):
        self.dashboard_page.stat_cards["credit_classes"].set_value(count)

    def _update_class_count(self, count):
        self.dashboard_page.stat_cards["classes"].set_value(count)

    def _update_student_count(self, count):
        self.dashboard_page.stat_cards["students"].set_value(count)
