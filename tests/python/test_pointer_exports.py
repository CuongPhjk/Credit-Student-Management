"""Pointer exports must remain independent Python snapshots after core data changes."""
import unittest
from bridge import (AppData, MonHoc, MonHocManager, Lop, SinhVien,
                    LopSinhVienManager, LopTinChi, LopTinChiManager, DangKyManager)


class PointerExportTest(unittest.TestCase):
    def test_snapshots_survive_clear_and_repeated_exports_do_not_own_nodes(self):
        data = AppData()
        subjects = MonHocManager(data)
        students = LopSinhVienManager(data)
        credits = LopTinChiManager(data)
        registrations = DangKyManager(data)
        subjects.them_mon_hoc(MonHoc("MH1", "Mon mot", 3, 0))
        students.them_lop(Lop("L1", "Lop mot"))
        students.them_sinh_vien("L1", SinhVien("SV1", "Le", "An", "Nam", "0901234567"))
        credits.them_lop_tin_chi(LopTinChi("MH1", "2026-2027", 1, 1, 1, 10))
        registrations.dang_ky(1, "SV1")
        for _ in range(3):
            mh = subjects.lay_danh_sach_mon_hoc()
            sv = students.lay_danh_sach_sinh_vien("L1")
            lop = students.lay_danh_sach_lop()
            ltc = credits.lay_danh_sach_lop_tin_chi()
            dk = registrations.lay_danh_sach_dang_ky(1)
            self.assertEqual((len(mh), len(sv), len(lop), len(ltc), len(dk)), (1, 1, 1, 1, 1))
        subjects.cap_nhat_mon_hoc("MH1", MonHoc("MH1", "Changed subject", 3, 0))
        students.cap_nhat_sinh_vien("SV1", SinhVien("SV1", "Le", "Binh", "Nam", "0912345678"))
        data.clear()
        self.assertEqual(subjects.tong_so_mon_hoc(), 0)
        self.assertEqual(students.tong_so_sinh_vien(), 0)
        self.assertEqual(credits.tong_so_lop_tin_chi(), 0)
        self.assertEqual(mh[0].ten_mh, "Mon mot")
        self.assertEqual(sv[0].ten, "An")
        self.assertEqual(lop[0].so_sinh_vien, 1)
        self.assertEqual(ltc[0].ma_mh, "MH1")
        self.assertEqual(dk[0]["ho_ten"], "Le An")
        self.assertEqual(subjects.lay_danh_sach_mon_hoc(), [])
        self.assertEqual(students.lay_danh_sach_sinh_vien("L1"), [])
        self.assertEqual(credits.lay_danh_sach_lop_tin_chi(), [])
        data.clear()


if __name__ == "__main__":
    unittest.main()
