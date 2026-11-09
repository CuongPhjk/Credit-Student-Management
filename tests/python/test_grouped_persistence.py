"""Grouped snapshots must preserve nested records and roll back failed saves."""
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from bridge import (AppData, MonHoc, MonHocManager, Lop, SinhVien,
                    LopSinhVienManager, LopTinChi, LopTinChiManager,
                    DangKyManager)

YEAR = f'{date.today().year}-{date.today().year + 1}'


class GroupedPersistenceTest(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.subject_file = self.root / 'monhoc.txt'
        self.student_file = self.root / 'lopsinhvien.txt'
        self.credit_file = self.root / 'loptinchi.txt'
        self.subject_file.write_text('MH1|Lập trình|3|1\nMH2|Cơ sở dữ liệu|2|1\n', encoding='utf-8')
        self.student_file.write_text(
            'L1|Lớp một\nSV1|Nguyễn Văn|An|Nam|0901234567\n'
            'SV2|Trần Thị|Bình|Nữ|0912345678\n#\nL2|Lớp rỗng\n#\n', encoding='utf-8')
        self.credit_file.write_text(
            f'1|MH1|{YEAR}|1|1|1|50|0\nSV1|0|0\n#\n'
            f'2|MH2|{YEAR}|1|1|1|50|0\n#\n', encoding='utf-8')
        self.data = AppData()
        # The registration manager predates loading but must share its save path.
        self.registrations = DangKyManager(self.data)
        self.subjects = MonHocManager(self.data)
        self.students = LopSinhVienManager(self.data)
        self.credits = LopTinChiManager(self.data)
        self.subjects.doc_danh_sach_mon_hoc(str(self.subject_file))
        self.students.doc_danh_sach_lop_sinh_vien(str(self.student_file))
        self.credits.doc_danh_sach_lop_tin_chi(str(self.credit_file))

    def tearDown(self):
        self.temp.cleanup()

    def snapshot(self):
        return {p.name: p.read_bytes() for p in self.root.glob('*.txt')}

    def test_interleaved_credit_registration_saves_preserve_children(self):
        untouched = (self.subject_file.read_bytes(), self.student_file.read_bytes())
        self.registrations.dang_ky(1, 'SV2')
        self.credits.cap_nhat_lop_tin_chi(1, LopTinChi('MH1', YEAR, 1, 1, 1, 60))
        self.registrations.huy_dang_ky(1, 'SV2')
        text = self.credit_file.read_text(encoding='utf-8')
        self.assertIn(f'1|MH1|{YEAR}|1|1|1|60|0\n', text)
        self.assertIn('SV1|0|0\n', text)
        self.assertIn('SV2|-1|1\n', text)
        self.credits.doc_danh_sach_lop_tin_chi(str(self.credit_file))
        self.assertTrue(self.registrations.da_dang_ky(1, 'SV1'))
        self.assertFalse(self.registrations.da_dang_ky(1, 'SV2'))
        self.assertEqual(untouched, (self.subject_file.read_bytes(), self.student_file.read_bytes()))
        self.assertEqual({p.name for p in self.root.iterdir()},
                         {'monhoc.txt', 'lopsinhvien.txt', 'loptinchi.txt'})

    def test_cancel_underfilled_classes_validates_preview_and_rolls_back_on_write_error(self):
        next_year = f'{date.today().year + 1}-{date.today().year + 2}'
        self.credit_file.write_text(
            f'1|MH1|{YEAR}|1|1|1|50|0\nSV1|0|0\n#\n'
            f'2|MH2|{YEAR}|1|1|1|50|0\n#\n'
            f'3|MH1|{YEAR}|1|2|2|50|0\nSV2|0|0\nSV1|-1|1\n#\n'
            f'4|MH1|{YEAR}|2|1|2|50|0\n#\n'
            f'5|MH1|{next_year}|1|1|2|50|0\n#\n'
            f'6|MH2|{YEAR}|1|2|2|50|1\n#\n',
            encoding='utf-8',
        )
        self.credits.doc_danh_sach_lop_tin_chi(str(self.credit_file))
        original = self.credit_file.read_bytes()
        preview = self.credits.lay_lop_thieu_si_so(YEAR, 1)
        self.assertEqual(preview, [(2, 'MH2', 1, 0, 1), (3, 'MH1', 2, 1, 2)])
        self.assertEqual(self.credit_file.read_bytes(), original)
        self.assertFalse(self.credits.tim_lop_tin_chi(3).huy_lop)

        self.registrations.dang_ky(2, 'SV2')
        self.credits.them_lop_tin_chi(LopTinChi('MH2', YEAR, 1, 3, 2, 50))
        before = self.credit_file.read_bytes()
        with self.assertRaisesRegex(ValueError, 'đã thay đổi'):
            self.credits.huy_lop_thieu_si_so(YEAR, 1, [2, 3])
        self.assertEqual(self.credit_file.read_bytes(), before)

        blocker = Path(str(self.credit_file) + '.tmp')
        blocker.mkdir()
        with self.assertRaises(ValueError):
            self.credits.huy_lop_thieu_si_so(YEAR, 1, [3, 7])
        self.assertEqual(self.credit_file.read_bytes(), before)
        self.assertFalse(self.credits.tim_lop_tin_chi(3).huy_lop)
        self.assertFalse(self.credits.tim_lop_tin_chi(7).huy_lop)
        blocker.rmdir()

        self.credits.huy_lop_thieu_si_so(YEAR, 1, [3, 7])
        self.credits.doc_danh_sach_lop_tin_chi(str(self.credit_file))
        cancelled = [row.ma_lop_tc for row in self.credits.lay_danh_sach_lop_tin_chi() if row.huy_lop]
        self.assertEqual(cancelled, [3, 6, 7])
        registrations = self.registrations.lay_danh_sach_dang_ky(3)
        self.assertEqual([(row['ma_sv'], row['da_huy']) for row in registrations],
                         [('SV2', False), ('SV1', True)])
        self.assertEqual(self.credits.lay_lop_thieu_si_so(YEAR, 1), [])

    def test_student_and_class_crud_rewrites_only_the_combined_student_file(self):
        before = self.snapshot()
        self.students.them_sinh_vien('L2', SinhVien('SV3', 'Lê', 'Cường', 'Nam', '0923456789'))
        self.students.cap_nhat_lop('L2', 'Lớp hai')
        self.students.cap_nhat_sinh_vien('SV3', SinhVien('SV3', 'Lê Văn', 'Cường', 'Nam', '0934567890'))
        self.students.them_lop(Lop('L3', 'Lớp ba'))
        text = self.student_file.read_text(encoding='utf-8')
        self.assertIn('L2|Lớp hai\nSV3|Lê Văn|Cường|Nam|0934567890\n#\n', text)
        self.assertIn('L3|Lớp ba\n#\n', text)
        self.assertNotIn('L2|SV3', text)
        self.students.doc_danh_sach_lop_sinh_vien(str(self.student_file))
        self.assertEqual(self.students.tong_so_sinh_vien(), 3)
        self.students.xoa_sinh_vien('SV3')
        self.students.xoa_lop('L2')
        self.assertNotIn('SV3', self.student_file.read_text(encoding='utf-8'))
        self.assertNotIn('L2|', self.student_file.read_text(encoding='utf-8'))
        self.assertEqual(self.subject_file.read_bytes(), before['monhoc.txt'])
        self.assertEqual(self.credit_file.read_bytes(), before['loptinchi.txt'])

    def test_other_managers_share_paths_loaded_through_appdata(self):
        subjects = MonHocManager(self.data)
        students = LopSinhVienManager(self.data)
        subjects.them_mon_hoc(MonHoc('MH3', 'Mon ba', 3, 0))
        students.them_lop(Lop('L3', 'Lop ba'))
        self.assertIn('MH3|', self.subject_file.read_text(encoding='utf-8'))
        self.assertIn('L3|', self.student_file.read_text(encoding='utf-8'))

    def test_subject_add_rewrites_snapshot_instead_of_appending(self):
        before = self.snapshot()
        self.subjects.them_mon_hoc(MonHoc('AAA', 'Môn mới', 2, 0))
        self.assertTrue(self.subject_file.read_text(encoding='utf-8').startswith('AAA|'))
        self.subjects.doc_danh_sach_mon_hoc(str(self.subject_file))
        self.assertEqual(self.subjects.tong_so_mon_hoc(), 3)
        self.assertEqual(self.student_file.read_bytes(), before['lopsinhvien.txt'])
        self.assertEqual(self.credit_file.read_bytes(), before['loptinchi.txt'])

    def test_malformed_student_blocks_clear_memory_and_allow_retry(self):
        invalid = [
            'L3|Lớp ba\n',  # Missing terminator.
            '#\n',
            'SV3|Lê|An|Nam|0901234567\n#\n',  # Child without parent.
            'L3|Lớp ba\nSV3|Lê|An|Nam|0901234567\n#\nL4|Lớp bốn\nSV3|Lê|An|Nam|0901234567\n#\n',
            'L3|Lớp ba\nSV3|Lê|An|Nu|0901234567\n#\n',
        ]
        path = self.root / 'invalid-students.txt'
        for text in invalid:
            with self.subTest(text=text):
                self.students.doc_danh_sach_lop_sinh_vien(str(self.student_file))
                path.write_text(text, encoding='utf-8')
                with self.assertRaises(RuntimeError):
                    self.students.doc_danh_sach_lop_sinh_vien(str(path))
                self.assertEqual(self.students.tong_so_lop(), 0)
                self.assertEqual(self.students.tong_so_sinh_vien(), 0)
        self.students.doc_danh_sach_lop_sinh_vien(str(self.student_file))
        self.students.doc_danh_sach_lop_sinh_vien(str(self.student_file))
        self.assertEqual(self.students.tong_so_lop(), 2)
        self.assertEqual(self.students.tong_so_sinh_vien(), 2)
        # A failed read must not redirect future saves to the bad file.
        self.students.them_lop(Lop('L3', 'Lớp ba'))
        self.assertIn('L3|', self.student_file.read_text(encoding='utf-8'))

    def test_malformed_credit_blocks_clear_memory_and_allow_retry(self):
        header = f'3|MH1|{YEAR}|1|2|1|50|0\n'
        invalid = [header, '#\n', header + 'SV1|nan|0|1\n#\n',
                   header + 'SV1|8|2|1\n#\n',
                   header + 'SV1|8|0|1\nSV1|7|0|1\n#\n',
                   header + '#\n' + header + '#\n']
        path = self.root / 'invalid-credits.txt'
        for text in invalid:
            with self.subTest(text=text):
                self.credits.doc_danh_sach_lop_tin_chi(str(self.credit_file))
                path.write_text(text, encoding='utf-8')
                with self.assertRaises(RuntimeError):
                    self.credits.doc_danh_sach_lop_tin_chi(str(path))
                self.assertEqual(self.credits.tong_so_lop_tin_chi(), 0)
        self.credits.doc_danh_sach_lop_tin_chi(str(self.credit_file))
        self.credits.doc_danh_sach_lop_tin_chi(str(self.credit_file))
        self.assertEqual(self.credits.tong_so_lop_tin_chi(), 2)
        self.assertTrue(self.registrations.da_dang_ky(1, 'SV1'))
        self.registrations.dang_ky(1, 'SV2')
        self.assertIn('SV2|-1|0', self.credit_file.read_text(encoding='utf-8'))

    def test_failed_writes_roll_back_all_managers_and_preserve_files(self):
        before = self.snapshot()
        blockers = [Path(str(p) + '.tmp') for p in (self.subject_file, self.student_file, self.credit_file)]
        for path in blockers:
            path.mkdir()  # Opening this as a temporary output file must fail.
        operations = [
            lambda: self.subjects.them_mon_hoc(MonHoc('AAA', 'Môn mới', 2, 0)),
            lambda: self.students.them_lop(Lop('L3', 'Lớp ba')),
            lambda: self.students.them_sinh_vien('L2', SinhVien('SV3', 'Lê', 'An', 'Nam', '0901234567')),
            lambda: self.students.cap_nhat_lop('L1', 'Đổi tên'),
            lambda: self.students.cap_nhat_sinh_vien('SV2', SinhVien('SV2', 'Lê', 'Cường', 'Nam', '0923456789')),
            lambda: self.students.xoa_lop('L2'),
            lambda: self.students.xoa_sinh_vien('SV2'),
            lambda: self.credits.them_lop_tin_chi(LopTinChi('MH1', YEAR, 1, 2, 1, 50)),
            lambda: self.credits.cap_nhat_lop_tin_chi(1, LopTinChi('MH1', YEAR, 1, 1, 1, 60)),
            lambda: self.credits.xoa_lop_tin_chi(2),
            lambda: self.registrations.dang_ky(1, 'SV2'),
            lambda: self.registrations.huy_dang_ky(1, 'SV1'),
        ]
        for operation in operations:
            with self.assertRaises((ValueError, RuntimeError)):
                operation()
            self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.subjects.tong_so_mon_hoc(), 2)
        self.assertEqual(self.students.tong_so_lop(), 2)
        self.assertEqual(self.students.tong_so_sinh_vien(), 2)
        self.assertEqual(self.students.tim_lop('L1').ten_lop, 'Lớp một')
        self.assertEqual(self.students.tim_sinh_vien('SV2').ten, 'Bình')
        self.assertEqual(self.credits.tong_so_lop_tin_chi(), 2)
        self.assertEqual(self.credits.tim_lop_tin_chi(1).so_sv_max, 50)
        self.assertTrue(self.registrations.da_dang_ky(1, 'SV1'))
        self.assertFalse(self.registrations.da_dang_ky(1, 'SV2'))
        for path in blockers:
            path.rmdir()
        self.registrations.dang_ky(1, 'SV2')
        self.assertIn('SV2|-1|0', self.credit_file.read_text(encoding='utf-8'))
        self.credits.them_lop_tin_chi(LopTinChi('MH1', YEAR, 1, 2, 1, 50))
        self.assertIsNotNone(self.credits.tim_lop_tin_chi(3))

    def test_failed_replacement_cleans_temp_and_retains_in_memory_state(self):
        saved = self.credit_file.with_suffix('.original')
        self.credit_file.rename(saved)
        original = saved.read_bytes()
        self.credit_file.mkdir()  # Save can write .tmp, but cannot replace a directory.
        with self.assertRaises(ValueError):
            self.registrations.dang_ky(1, 'SV2')
        self.assertEqual(saved.read_bytes(), original)
        self.assertFalse(self.registrations.da_dang_ky(1, 'SV2'))
        self.assertFalse(Path(str(self.credit_file) + '.tmp').exists())
        self.credit_file.rmdir()
        saved.rename(self.credit_file)

    def test_empty_files_and_empty_blocks_are_valid(self):
        self.student_file.write_text('', encoding='utf-8')
        self.students.doc_danh_sach_lop_sinh_vien(str(self.student_file))
        self.students.them_lop(Lop('L3', 'Lớp ba'))
        self.assertEqual(self.student_file.read_text(encoding='utf-8'), 'L3|Lớp ba\n#\n')
        self.credit_file.write_text('', encoding='utf-8')
        self.credits.doc_danh_sach_lop_tin_chi(str(self.credit_file))
        self.credits.them_lop_tin_chi(LopTinChi('MH1', YEAR, 1, 1, 1, 50))
        self.assertTrue(self.credit_file.read_text(encoding='utf-8').endswith('\n#\n'))
        self.credits.doc_danh_sach_lop_tin_chi(str(self.credit_file))
        self.assertEqual(self.credits.tong_so_lop_tin_chi(), 1)


if __name__ == '__main__':
    unittest.main()
