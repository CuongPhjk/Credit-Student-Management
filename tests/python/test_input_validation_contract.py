"""Forms validate input; file readers validate records; core enforces business rules."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication
from bridge import AppData, MonHocManager, LopSinhVienManager, MonHoc, Lop, SinhVien
from frontend.pages.subject_page import SubjectForm
from frontend.pages.class_student_page import StudentForm


class InputValidationContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_form_blocks_invalid_subject_and_student_before_backend(self):
        callback = Mock()
        subject = SubjectForm(on_add=callback)
        subject.code_input.setText("BAD@")
        subject.name_input.setText("Mon hoc")
        subject._validate()
        callback.assert_not_called()
        self.assertTrue(subject.code_input.property("invalid"))
        student = StudentForm(on_add=callback)
        student.code_input.setText("SV1")
        student.surname_input.setText("Nguyen")
        student.given_name_input.setText("An")
        student.phone_input.setText("1234567890")
        student._validate_student()
        callback.assert_not_called()
        self.assertTrue(student.phone_input.property("invalid"))
        subject.close()
        student.close()

    def test_file_input_rejects_bad_records_and_clears_subject_tree(self):
        data = AppData()
        subjects, students = MonHocManager(data), LopSinhVienManager(data)
        subjects.them_mon_hoc(MonHoc("MH1", "Mon mot", 3, 0))
        students.them_lop(Lop("L1", "Lop mot"))
        with TemporaryDirectory() as temp:
            path = Path(temp) / "invalid.txt"
            for text in ("TOOLONGCODE123|Mon|3|0\n", "MH2||3|0\n", "MH2|Mon|0|0\n", "MH2|Mon|3|-1\n"):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(RuntimeError):
                    subjects.doc_danh_sach_mon_hoc(str(path))
                self.assertEqual(subjects.tong_so_mon_hoc(), 0)
            for text in ("TOOLONGCLASSCODE123|Lop\n#\n", "L2|Lop\nSV2|Le|An|Nu|0901234567\n#\n", "L2|Lop\nSV2|Le|An|Nam|1234567890\n#\n"):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(RuntimeError):
                    students.doc_danh_sach_lop_sinh_vien(str(path))
                self.assertEqual(students.tong_so_lop(), 0)

    def test_subject_read_replaces_tree_clears_partial_data_and_can_retry(self):
        data = AppData()
        subjects = MonHocManager(data)
        subjects.them_mon_hoc(MonHoc("OLD", "Old subject", 3, 0))
        with TemporaryDirectory() as temp:
            path = Path(temp) / "subjects.txt"
            # A failure to open must leave existing data intact.
            with self.assertRaises(RuntimeError):
                subjects.doc_danh_sach_mon_hoc(str(path))
            self.assertIsNotNone(subjects.tim_mon_hoc("OLD"))
            path.write_text("MH1|Subject one|3|0\nBAD\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "2"):
                subjects.doc_danh_sach_mon_hoc(str(path))
            self.assertEqual(subjects.tong_so_mon_hoc(), 0)
            path.write_text("MH1|Subject one|3|0\nMH2|Subject two|2|0\n", encoding="utf-8")
            subjects.doc_danh_sach_mon_hoc(str(path))
            subjects.doc_danh_sach_mon_hoc(str(path))
            self.assertEqual(subjects.tong_so_mon_hoc(), 2)
            self.assertIsNone(subjects.tim_mon_hoc("OLD"))
            self.assertIsNotNone(subjects.tim_mon_hoc("MH2"))
            # Duplicate records also clear nodes already read.
            path.write_text("MH1|Subject one|3|0\nMH1|Duplicate|2|0\n", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                subjects.doc_danh_sach_mon_hoc(str(path))
            self.assertEqual(subjects.tong_so_mon_hoc(), 0)
            path.write_text("", encoding="utf-8")
            subjects.doc_danh_sach_mon_hoc(str(path))
            self.assertEqual(subjects.tong_so_mon_hoc(), 0)

    def test_core_trusts_form_but_still_rejects_duplicates(self):
        data = AppData()
        students = LopSinhVienManager(data)
        students.them_lop(Lop("L1", "Lop mot"))
        # Deliberately bypass the form to demonstrate its responsibility.
        item = SinhVien("S"*16, "Le", "An", "Nam", "0901234567")
        students.them_sinh_vien("L1", item)
        with self.assertRaisesRegex(ValueError, "đã tồn tại"):
            students.them_sinh_vien("L1", item)
        self.assertEqual(students.tong_so_sinh_vien(), 1)


if __name__ == "__main__":
    unittest.main()
