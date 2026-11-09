"""Sort UI, borrowed cache lifetime and persistence-failure integration checks."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from PyQt6.QtWidgets import QApplication, QStackedWidget, QWidget
from bridge import AppData, LopSinhVienManager, Lop, SinhVien
from frontend.pages.class_student_page import ClassStudentPage


class StudentSortingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.data = AppData()
        self.manager = LopSinhVienManager(self.data)
        self.manager.them_lop(Lop("L1", "Lop mot"))
        self.manager.them_lop(Lop("L2", "Lop hai"))
        for code, name in [("SV3", "An"), ("SV1", "Cuong"), ("SV2", "Binh")]:
            self.manager.them_sinh_vien("L1", SinhVien(code, "Le", name, "Nam", "0901234567"))
        self.page = ClassStudentPage(self.manager)
        self.stack = QStackedWidget()
        self.stack.addWidget(self.page)
        self.stack.addWidget(QWidget())
        self.stack.resize(1200, 800)
        self.stack.show()
        self.page.open_student_list("L1")
        self.app.processEvents()

    def tearDown(self):
        self.stack.close()
        self.stack.deleteLater()
        self.app.processEvents()

    def codes(self):
        return [self.page.student_table.item(row, 1).text() for row in range(self.page.student_table.rowCount())]

    def test_descending_first_toggle_name_and_return_to_page(self):
        self.assertEqual(self.codes(), ["SV3", "SV2", "SV1"])
        self.page.student_sort.setCurrentIndex(2)
        self.assertEqual(self.codes(), ["SV3", "SV2", "SV1"])
        self.page.student_sort.setCurrentIndex(1)
        self.assertEqual(self.codes(), ["SV1", "SV2", "SV3"])
        self.page.student_sort.setCurrentIndex(0)
        self.assertEqual(self.codes(), ["SV3", "SV2", "SV1"])
        self.page.student_sort.setCurrentIndex(1)
        self.stack.setCurrentIndex(1)
        self.app.processEvents()
        self.stack.setCurrentIndex(0)
        self.page.refresh()
        self.assertEqual(self.page.student_sort.currentData(), "code_asc")
        self.assertEqual(self.codes(), ["SV1", "SV2", "SV3"])
        self.manager.cap_nhat_sinh_vien("SV3", SinhVien("SV3", "Le", "Zung", "Nam", "0901234567"))
        self.page.refresh_students()
        self.assertEqual(self.codes(), ["SV1", "SV2", "SV3"])
        self.assertEqual(self.page.student_table.item(2, 3).text(), "Zung")
        self.assertEqual([sv.ma_sv for sv in self.manager.lay_danh_sach_sinh_vien("L1")], ["SV2", "SV1", "SV3"])

    def test_search_is_button_only_and_pagination_uses_selected_order(self):
        self.page.STUDENT_PAGE_SIZE = 2
        self.page.student_sort.setCurrentIndex(1)
        self.assertEqual(self.codes(), ["SV1", "SV2"])
        self.page.current_student_page = 2
        self.page.apply_student_filter(reset_page=False)
        self.assertEqual(self.codes(), ["SV3"])
        self.page.student_sort.setCurrentIndex(2)
        self.assertEqual(self.codes(), ["SV3", "SV2"])
        self.page.student_search_input.setText("SV1")
        self.assertEqual(self.codes(), ["SV3", "SV2"])
        self.page.student_search_button.click()
        self.assertEqual(self.codes(), ["SV1"])
        self.page.student_sort.setCurrentIndex(1)
        self.assertEqual(self.codes(), ["SV1"])
        self.page.student_search_input.setText("missing")
        self.page.student_search_button.click()
        self.assertEqual(self.codes(), [])
        self.page.show_class_list()
        self.page.open_student_list("L2")
        self.assertEqual(self.page.student_sort.currentData(), "name")
        self.assertEqual(self.codes(), [])

    def test_shared_manager_reload_same_count_clear_and_failed_delete(self):
        other = LopSinhVienManager(self.data)
        self.assertEqual([sv.ma_sv for sv in self.manager.lay_sinh_vien_ma_giam("L1")], ["SV3", "SV2", "SV1"])
        with TemporaryDirectory() as directory:
            path = Path(directory) / "students.txt"
            path.write_text("L1|Lop mot\nSV4|Le|An|Nam|0901234567\nSV5|Le|Binh|Nam|0901234567\nSV6|Le|Cuong|Nam|0901234567\n#\n", encoding="utf-8")
            other.doc_danh_sach_lop_sinh_vien(str(path))
            self.assertEqual([sv.ma_sv for sv in self.manager.lay_sinh_vien_ma_tang("L1")], ["SV4", "SV5", "SV6"])
            Path(str(path) + ".tmp").mkdir()
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                other.xoa_sinh_vien("SV5")
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(self.manager.tong_so_sinh_vien_trong_lop("L1"), 3)
            self.assertEqual([sv.ma_sv for sv in self.manager.lay_sinh_vien_ma_giam("L1")], ["SV6", "SV5", "SV4"])
            path.write_text("L1|Lop mot\nBAD\n", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                other.doc_danh_sach_lop_sinh_vien(str(path))
            self.assertEqual(self.manager.lay_sinh_vien_ma_tang("L1"), [])
        self.data.clear()
        self.assertEqual(self.manager.lay_sinh_vien_ma_giam("L1"), [])
        other.them_lop(Lop("L1", "New class"))
        other.them_sinh_vien("L1", SinhVien("NEW", "Le", "An", "Nam", "0901234567"))
        self.assertEqual([sv.ma_sv for sv in self.manager.lay_sinh_vien_ma_tang("L1")], ["NEW"])


if __name__ == "__main__":
    unittest.main()
