from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from bridge import (
    AppData,
    DangKyManager,
    DiemManager,
    LopSinhVienManager,
    LopTinChiManager,
    MonHocManager,
)


DATA_DIR = Path(__file__).resolve().parents[2] / "backend" / "data"


def _load_base_data(registration_file):
    data = AppData()
    subject_manager = MonHocManager(data)
    credit_class_manager = LopTinChiManager(data)
    student_manager = LopSinhVienManager(data)
    registration_manager = DangKyManager(data)
    score_manager = DiemManager(data)

    subject_manager.doc_danh_sach_mon_hoc(str(DATA_DIR / "monhoc.txt"))
    # Each test owns its credit-class snapshot; mutations never touch sample data.
    registration_file.write_text(
        "1|INT118|2026-2027|1|1|20|50|0\n#\n"
        "2|INT109|2026-2027|1|1|26|45|0\n#\n"
        "3|INT115|2026-2027|1|1|20|40|1\n#\n", encoding="utf-8"
    )
    credit_class_manager.doc_danh_sach_lop_tin_chi(str(registration_file))
    student_manager.doc_danh_sach_lop_sinh_vien(str(DATA_DIR / "lopsinhvien.txt"))
    return data, registration_manager, score_manager


class ScoreBridgeTest(unittest.TestCase):
    def test_score_filter_update_and_persist(self):
        with TemporaryDirectory() as directory:
            registration_file = Path(directory) / "loptinchi.txt"
            registration_file.write_text("", encoding="utf-8")
            data, registration_manager, score_manager = _load_base_data(
                registration_file
            )

            registration_manager.dang_ky(1, "N21DCCN001")
            rows = score_manager.lay_danh_sach_sinh_vien(
                "2026-2027", 1, "INT118", 1
            )
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["ma_sv"], "N21DCCN001")
            self.assertEqual(rows[0]["diem"], 0)
            self.assertFalse(rows[0]["da_co_diem"])

            score_manager.cap_nhat_danh_sach_diem(
                "2026-2027",
                1,
                "INT118",
                1,
                [{"ma_sv": "N21DCCN001", "diem": 8.75}],
            )
            rows = score_manager.lay_danh_sach_sinh_vien(
                "2026-2027", 1, "INT118", 1
            )
            self.assertAlmostEqual(rows[0]["diem"], 8.75)
            self.assertTrue(rows[0]["da_co_diem"])
            self.assertIn(
                "N21DCCN001|8.75|0|1",
                registration_file.read_text(encoding="utf-8"),
            )

            with self.assertRaisesRegex(ValueError, "0 den 10"):
                score_manager.cap_nhat_danh_sach_diem(
                    "2026-2027",
                    1,
                    "INT118",
                    1,
                    [{"ma_sv": "N21DCCN001", "diem": 11}],
                )
            del score_manager, registration_manager, data

    def test_score_rejects_cancelled_class(self):
        with TemporaryDirectory() as directory:
            registration_file = Path(directory) / "loptinchi.txt"
            registration_file.write_text("", encoding="utf-8")
            data, registration_manager, score_manager = _load_base_data(
                registration_file
            )

            with self.assertRaisesRegex(ValueError, "da bi huy"):
                score_manager.lay_danh_sach_sinh_vien(
                    "2026-2027", 1, "INT115", 1
                )
            del score_manager, registration_manager, data


if __name__ == "__main__":
    unittest.main()
