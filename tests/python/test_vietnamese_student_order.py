"""Vietnamese name order through add/edit/load and the Python bridge."""
from itertools import permutations
from pathlib import Path
from tempfile import TemporaryDirectory
import unicodedata
import unittest
from bridge import AppData, LopSinhVienManager, Lop, SinhVien


class VietnameseStudentOrderTest(unittest.TestCase):
    def test_add_order_and_unicode_forms_do_not_change_sort(self):
        expected = ["An", "Bảo", "Bình", "Đạt"]
        for form in ("NFC", "NFD"):
            for order in permutations(expected):
                with self.subTest(form=form, order=order):
                    data = AppData()
                    manager = LopSinhVienManager(data)
                    manager.them_lop(Lop("L1", "Lớp một"))
                    for i, name in enumerate(order):
                        manager.them_sinh_vien("L1", SinhVien("SV"+str(i), "lÊ", unicodedata.normalize(form, name.upper()), "Nam", "0901234567"))
                    self.assertEqual([s.ten for s in manager.lay_danh_sach_sinh_vien("L1")], expected)
                    self.assertEqual({s.ho for s in manager.lay_danh_sach_sinh_vien("L1")}, {"Lê"})

    def test_edit_and_reload_reinsert_names_in_vietnamese_order(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "students.txt"
            path.write_text("L1|Lớp một\nSV1|Nguyễn Tiến|Bình|Nam|0901234567\nSV2|Lê Tiến|Bảo|Nam|0901234568\n#\n", encoding="utf-8")
            data = AppData()
            manager = LopSinhVienManager(data)
            manager.doc_danh_sach_lop_sinh_vien(str(path))
            self.assertEqual([s.ten for s in manager.lay_danh_sach_sinh_vien("L1")], ["Bảo", "Bình"])
            manager.cap_nhat_sinh_vien("SV1", SinhVien("SV1", "ĐẶNG QUỐC", "ÁNH", "Nam", "0901234567"))
            self.assertEqual([s.ten for s in manager.lay_danh_sach_sinh_vien("L1")], ["Ánh", "Bảo"])
            manager.doc_danh_sach_lop_sinh_vien(str(path))
            self.assertEqual([s.ten for s in manager.lay_danh_sach_sinh_vien("L1")], ["Ánh", "Bảo"])


if __name__ == "__main__":
    unittest.main()
