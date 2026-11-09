"""Integration checks for registration lists and persisted registration data."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtWidgets import QApplication, QLabel
from bridge import AppData, MonHocManager, LopSinhVienManager, LopTinChiManager, DangKyManager, LopTinChi
from frontend.pages.credit_class_page import CreditClassPage
from frontend.pages.class_student_page import ClassStudentPage
from frontend.pages.registration_page import AvailableClassTable

YEAR = f"{date.today().year}-{date.today().year + 1}"


class RegistrationWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        for font in ("segoeui.ttf", "segoeuib.ttf"):
            QFontDatabase.addApplicationFont(str(Path("C:/Windows/Fonts") / font))
        cls.app.setFont(QFont("Segoe UI", 10))

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.credit_file = self.root / "credits.txt"
        (self.root / "subjects.txt").write_text("MH1|Môn một|3|0\nMH2|Môn hai|3|0\n", encoding="utf-8")
        (self.root / "students.txt").write_text(
            "L1|Lớp một\nSV1|Nguyễn Văn|An|Nam|0901234567\n"
            "SV2|Trần Thị|Bình|Nữ|0912345678\nSV3|Lê|Cường|Nam|0923456789\n#\n", encoding="utf-8")
        self.credit_file.write_text(
            f"1|MH1|{YEAR}|1|1|1|3|0\nSV1|-1|0\nSV3|8|1\n#\n"
            f"2|MH1|{YEAR}|1|2|1|2|0\n#\n"
            f"3|MH2|{YEAR}|1|1|1|1|0\nSV1|0|0\n#\n", encoding="utf-8")
        self.data = AppData()
        self.subjects = MonHocManager(self.data)
        self.students = LopSinhVienManager(self.data)
        self.credits = LopTinChiManager(self.data)
        self.registrations = DangKyManager(self.data)
        self.subjects.doc_danh_sach_mon_hoc(str(self.root / "subjects.txt"))
        self.students.doc_danh_sach_lop_sinh_vien(str(self.root / "students.txt"))
        self.credits.doc_danh_sach_lop_tin_chi(str(self.credit_file))
        self.pages = []

    def tearDown(self):
        for page in self.pages:
            page.close()
            page.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def test_append_order_and_double_click_view_include_cancelled(self):
        self.registrations.dang_ky(1, "SV2")
        rows = self.registrations.lay_danh_sach_dang_ky(1)
        self.assertEqual([r["ma_sv"] for r in rows], ["SV1", "SV3", "SV2"])
        self.assertEqual(rows[1]["ho_ten"], "Lê Cường")
        self.assertTrue(rows[1]["da_huy"])
        page = CreditClassPage(self.credits, subject_manager=self.subjects)
        page.registration_manager = self.registrations
        self.pages.append(page)
        page.table.cellDoubleClicked.emit(0, 0)
        self.assertEqual(page.registration_stack.currentIndex(), 1)
        self.assertEqual(page.registration_table.columnCount(), 3)
        self.assertEqual(page.registration_table.rowCount(), 3)
        self.assertEqual(page.registration_table.item(1, 2).text(), "Đã hủy")
        page.resize(1200, 800)
        page.show()
        self.app.processEvents()
        page.grab().save("build/registration-students-updated.png")

    def test_registration_search_only_applies_on_button_click(self):
        page = CreditClassPage(self.credits, subject_manager=self.subjects)
        page.registration_manager = self.registrations
        self.pages.append(page)
        page.open_registrations(1)
        self.assertEqual(page.registration_table.rowCount(), 2)
        active = page.registration_table.cellWidget(0, 2).findChild(QLabel)
        cancelled = page.registration_table.cellWidget(1, 2).findChild(QLabel)
        self.assertIn("#15803d", active.styleSheet())
        self.assertIn("#dc2626", cancelled.styleSheet())
        page.registration_search_input.setText("cường")
        self.assertEqual(page.registration_table.rowCount(), 2)
        page.registration_search_button.click()
        self.assertEqual(page.registration_table.rowCount(), 1)
        self.assertEqual(page.registration_table.item(0, 0).text(), "SV3")
        page.registration_search_input.clear()
        self.assertEqual(page.registration_table.rowCount(), 1)
        page.registration_search_button.click()
        self.assertEqual(page.registration_table.rowCount(), 2)
        page.registration_search_input.setText("missing")
        page.registration_search_button.click()
        self.assertEqual(page.registration_table.rowCount(), 0)
        page.open_registrations(3)
        self.assertEqual(page.registration_search_input.text(), "")
        self.assertEqual(page.registration_table.rowCount(), 1)

    def test_student_search_only_applies_on_button_click_and_retains_submitted_text(self):
        page = ClassStudentPage(self.students)
        self.pages.append(page)
        page.open_student_list("L1")
        self.assertEqual(page.student_table.rowCount(), 3)
        page.student_search_input.setText("Bình")
        self.assertEqual(page.student_table.rowCount(), 3)
        page.student_search_button.click()
        self.assertEqual(page.student_table.rowCount(), 1)
        self.assertEqual(page.student_table.item(0, 1).text(), "SV2")
        page.student_search_input.setText("SV1")
        page.refresh_students()
        self.assertEqual(page.student_table.item(0, 1).text(), "SV2")
        page.student_search_button.click()
        self.assertEqual(page.student_table.item(0, 1).text(), "SV1")
        page.student_search_input.clear()
        self.assertEqual(page.student_table.rowCount(), 1)
        page.student_search_button.click()
        self.assertEqual(page.student_table.rowCount(), 3)

    def test_selection_enabled_backend_rejects_duplicate_and_full(self):
        table = AvailableClassTable()
        self.pages.append(table)
        classes = list(self.credits.lay_danh_sach_lop_tin_chi())
        table.set_classes(classes, {"MH1": "Môn một", "MH2": "Môn hai"})
        self.assertEqual(table.columnCount(), 6)
        self.assertTrue(all(button.isEnabled() for button in table.button_group.buttons()))
        with self.assertRaisesRegex(ValueError, "đã đăng ký lớp tín chỉ này"):
            self.registrations.dang_ky(1, "SV1")
        with self.assertRaisesRegex(ValueError, "cùng học kỳ"):
            self.registrations.dang_ky(2, "SV1")
        with self.assertRaisesRegex(ValueError, "hết chỗ"):
            self.registrations.dang_ky(3, "SV2")

    def test_legacy_ungraded_and_zero_migrate_without_losing_distinction(self):
        self.credit_file.write_text(
            f"1|MH1|{YEAR}|1|1|1|3|0\nSV1|0|0|0\nSV2|0|0|1\n#\n", encoding="utf-8")
        self.credits.doc_danh_sach_lop_tin_chi(str(self.credit_file))
        self.credits.cap_nhat_lop_tin_chi(
            1, LopTinChi("MH1", YEAR, 1, 1, 1, 3)
        )
        self.assertIn("SV1|-1|0\nSV2|0|0\n", self.credit_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
