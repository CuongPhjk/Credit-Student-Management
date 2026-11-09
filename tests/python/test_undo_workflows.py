"""Undo qua manager, luu file va giao dien; chi dung du lieu trong thu muc tam."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from bridge import (
    AppData, MonHoc, MonHocManager, Lop, SinhVien, LopSinhVienManager,
    LopTinChi, LopTinChiManager, DangKyManager,
)
from frontend.components.topbar import TopBar
from frontend.main_window import MainWindow


class UndoWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.files = {
            "monhoc.txt": "MH1|Mon mot|3|0\nMH2|Mon hai|2|1\n",
            "lopsinhvien.txt": (
                "L1|Lop mot\nSV1|Nguyen|An|Nam|0901234567\n"
                "SV2|Tran|Binh|Nam|0901234568\n#\nL2|Lop hai\n#\nL3|Lop ba\n#\n"
            ),
            "loptinchi.txt": (
                "1|MH1|2026-2027|1|1|3|10|0\nSV1|-1|0\nSV2|8|1\n#\n"
                "2|MH2|2026-2027|1|1|2|10|0\n#\n"
            ),
        }
        for name, content in self.files.items():
            (self.root / name).write_text(content, encoding="utf-8")
        self.data = AppData()
        self.subjects = MonHocManager(self.data)
        self.students = LopSinhVienManager(self.data)
        self.credits = LopTinChiManager(self.data)
        self.registrations = DangKyManager(self.data)
        self.subjects.doc_danh_sach_mon_hoc(str(self.root / "monhoc.txt"))
        self.students.doc_danh_sach_lop_sinh_vien(str(self.root / "lopsinhvien.txt"))
        self.credits.doc_danh_sach_lop_tin_chi(str(self.root / "loptinchi.txt"))

    def tearDown(self):
        self.temp.cleanup()

    def text(self, filename):
        return (self.root / filename).read_text(encoding="utf-8")

    def test_global_lifo_across_managers_and_new_action_after_undo(self):
        self.subjects.them_mon_hoc(MonHoc(" mh3 ", "Mon ba", 3, 0))
        self.students.them_lop(Lop(" l4 ", "Lop bon"))
        self.students.them_sinh_vien("L4", SinhVien(" sv3 ", "Le", "Chi", "Nam", "0901234569"))
        self.credits.them_lop_tin_chi(LopTinChi("MH3", "2026-2027", 1, 1, 1, 10))
        self.registrations.dang_ky(3, "SV3")
        self.assertEqual(self.data.so_thao_tac_undo, 5)
        self.assertIn("SV3", self.data.mo_ta_undo)
        self.data.undo()
        self.assertEqual(self.registrations.lay_danh_sach_dang_ky(3), [])
        self.data.undo()
        self.assertIsNone(self.credits.tim_lop_tin_chi(3))
        # Undo phuc hoi ca bo dem ma tu sinh.
        self.credits.them_lop_tin_chi(LopTinChi("MH3", "2026-2027", 1, 2, 1, 10))
        self.assertIsNotNone(self.credits.tim_lop_tin_chi(3))
        self.data.undo()
        self.data.undo()
        self.assertIsNone(self.students.tim_sinh_vien("SV3"))
        self.data.undo()
        self.assertIsNone(self.students.tim_lop("L4"))
        self.data.undo()
        self.assertIsNone(self.subjects.tim_mon_hoc("MH3"))
        self.assertEqual(self.data.so_thao_tac_undo, 0)
        for filename, original in self.files.items():
            self.assertEqual(self.text(filename), original)

    def test_subject_edit_delete_and_sorted_cache(self):
        self.subjects.them_mon_hoc(MonHoc("MH3", "Mon ba", 3, 0))
        self.data.clear_undo()
        self.subjects.cap_nhat_mon_hoc(" mh3 ", MonHoc("MH3", "A", 1, 2))
        self.subjects.lay_mon_hoc_theo_ten()
        self.subjects.xoa_mon_hoc(" mh3 ")
        self.subjects.lay_mon_hoc_theo_ten()
        self.data.undo()
        self.assertEqual(self.subjects.lay_mon_hoc_theo_ten()[0].ten_mh, "A")
        self.data.undo()
        restored = self.subjects.tim_mon_hoc("MH3")
        self.assertEqual((restored.ten_mh, restored.stc_lt, restored.stc_th), ("Mon ba", 3, 0))
        self.assertEqual(len(self.subjects.lay_mon_hoc_theo_ten()), 3)

    def test_class_delete_restores_array_position_and_edit_keeps_students(self):
        self.students.xoa_lop("L2")
        self.data.undo()
        self.assertEqual([x.ma_lop for x in self.students.lay_danh_sach_lop()], ["L1", "L2", "L3"])
        self.students.cap_nhat_lop("L1", "Ten moi")
        self.data.undo()
        self.assertEqual(self.students.tim_lop("L1").ten_lop, "Lop mot")
        self.assertEqual(self.students.tong_so_sinh_vien_trong_lop("L1"), 2)
        self.assertEqual(self.text("lopsinhvien.txt"), self.files["lopsinhvien.txt"])

    def test_student_delete_edit_restore_order_counts_and_shared_cache(self):
        second = LopSinhVienManager(self.data)
        self.students.them_sinh_vien("L1", SinhVien("SV3", "Le", "Chi", "Nam", "0901234569"))
        self.data.clear_undo()
        self.students.cap_nhat_sinh_vien("SV3", SinhVien("IGNORED", "Le", "A", "Nữ", "0909999999"))
        second.lay_sinh_vien_ma_tang("L1")
        self.students.xoa_sinh_vien("SV3")
        second.lay_sinh_vien_ma_tang("L1")
        self.data.undo()
        self.assertEqual([x.ma_sv for x in second.lay_sinh_vien_ma_tang("L1")], ["SV1", "SV2", "SV3"])
        self.assertEqual(self.students.lay_danh_sach_sinh_vien("L1")[0].ma_sv, "SV3")
        self.data.undo()
        self.assertEqual([x.ma_sv for x in self.students.lay_danh_sach_sinh_vien("L1")], ["SV1", "SV2", "SV3"])
        restored = self.students.tim_sinh_vien("SV3")
        self.assertEqual((restored.ten, restored.phai, restored.so_dt), ("Chi", "Nam", "0901234569"))
        self.assertEqual(self.students.tong_so_sinh_vien_trong_lop("L1"), 3)
        self.assertEqual([x.ma_sv for x in second.lay_sinh_vien_ma_giam("L1")], ["SV3", "SV2", "SV1"])

    def test_credit_class_edit_delete_and_batch_cancel_restore_registrations(self):
        self.credits.cap_nhat_lop_tin_chi(1, LopTinChi("MH1", "2026-2027", 1, 1, 4, 12))
        self.credits.huy_lop_thieu_si_so("2026-2027", 1, [1, 2])
        self.assertEqual(self.data.so_thao_tac_undo, 2)
        self.data.undo()
        self.assertFalse(self.credits.tim_lop_tin_chi(1).huy_lop)
        self.assertFalse(self.credits.tim_lop_tin_chi(2).huy_lop)
        self.data.undo()
        self.assertEqual(self.text("loptinchi.txt"), self.files["loptinchi.txt"])
        self.credits.xoa_lop_tin_chi(2)
        self.data.undo()
        self.assertEqual([x.ma_lop_tc for x in self.credits.lay_danh_sach_lop_tin_chi()], [1, 2])
        self.assertEqual(self.text("loptinchi.txt"), self.files["loptinchi.txt"])

    def test_registration_reactivation_and_cancellation_keep_score_and_order(self):
        self.registrations.dang_ky(1, " sv2 ")
        self.assertTrue(self.registrations.da_dang_ky(1, "SV2"))
        self.data.undo()
        self.assertEqual(self.text("loptinchi.txt"), self.files["loptinchi.txt"])
        self.registrations.huy_dang_ky(1, "SV1")
        self.assertFalse(self.registrations.da_dang_ky(1, "SV1"))
        self.data.undo()
        self.assertTrue(self.registrations.da_dang_ky(1, "SV1"))
        self.assertEqual(self.text("loptinchi.txt"), self.files["loptinchi.txt"])

    def test_noop_and_rejected_operations_do_not_push(self):
        self.students.cap_nhat_lop("L1", " Lop  mot ")
        self.students.cap_nhat_sinh_vien("SV1", self.students.tim_sinh_vien("SV1"))
        self.subjects.cap_nhat_mon_hoc("MH1", self.subjects.tim_mon_hoc("MH1"))
        self.credits.cap_nhat_lop_tin_chi(1, self.credits.tim_lop_tin_chi(1))
        for action in (
            lambda: self.subjects.them_mon_hoc(MonHoc("MH1", "Trung", 3, 0)),
            lambda: self.subjects.xoa_mon_hoc("MH1"),
            lambda: self.students.xoa_lop("L1"),
            lambda: self.students.xoa_sinh_vien("SV1"),
            lambda: self.credits.xoa_lop_tin_chi(1),
            lambda: self.registrations.dang_ky(1, "SV1"),
        ):
            with self.assertRaises(ValueError):
                action()
        self.assertEqual(self.data.so_thao_tac_undo, 0)
        self.assertEqual(self.data.mo_ta_undo, "")
        with self.assertRaisesRegex(ValueError, "Không có thao tác"):
            self.data.undo()

    def test_save_failure_does_not_push_and_failed_undo_can_be_retried(self):
        self.subjects.them_mon_hoc(MonHoc("MH3", "Mon ba", 3, 0))
        current = self.text("monhoc.txt")
        # Chan tep .tmp de gay loi luu that, khong sua du lieu cua project.
        blocker = self.root / "monhoc.txt.tmp"
        blocker.mkdir()
        with self.assertRaises(ValueError):
            self.subjects.them_mon_hoc(MonHoc("MH4", "Mon bon", 3, 0))
        self.assertIsNone(self.subjects.tim_mon_hoc("MH4"))
        with self.assertRaises(ValueError):
            self.data.undo()
        self.assertEqual(self.data.so_thao_tac_undo, 1)
        self.assertIsNotNone(self.subjects.tim_mon_hoc("MH3"))
        self.assertEqual(self.text("monhoc.txt"), current)
        blocker.rmdir()
        self.data.undo()
        self.assertEqual(self.text("monhoc.txt"), self.files["monhoc.txt"])

    def test_failed_undo_restores_students_credit_ids_and_batch_flags(self):
        self.students.xoa_lop("L2")
        blocker = self.root / "lopsinhvien.txt.tmp"
        blocker.mkdir()
        with self.assertRaises(ValueError):
            self.data.undo()
        self.assertIsNone(self.students.tim_lop("L2"))
        blocker.rmdir()
        self.data.undo()
        self.credits.huy_lop_thieu_si_so("2026-2027", 1, [1, 2])
        blocker = self.root / "loptinchi.txt.tmp"
        blocker.mkdir()
        with self.assertRaises(ValueError):
            self.data.undo()
        self.assertTrue(all(x.huy_lop for x in self.credits.lay_danh_sach_lop_tin_chi()))
        self.assertEqual(self.data.so_thao_tac_undo, 1)
        blocker.rmdir()
        self.data.undo()
        self.assertEqual(self.text("loptinchi.txt"), self.files["loptinchi.txt"])

    def test_reload_clear_and_separate_appdata_reset_history(self):
        for manager, method, filename in (
            (self.subjects, "doc_danh_sach_mon_hoc", "monhoc.txt"),
            (self.students, "doc_danh_sach_lop_sinh_vien", "lopsinhvien.txt"),
            (self.credits, "doc_danh_sach_lop_tin_chi", "loptinchi.txt"),
        ):
            self.students.cap_nhat_lop("L1", filename)
            getattr(manager, method)(str(self.root / filename))
            self.assertEqual(self.data.so_thao_tac_undo, 0)
        self.students.cap_nhat_lop("L1", "Ten moi")
        other = AppData()
        self.assertEqual(other.so_thao_tac_undo, 0)
        self.data.clear()
        self.assertEqual(self.data.so_thao_tac_undo, 0)
        self.assertEqual(self.students.tong_so_lop(), 0)


class UndoWindowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in ("monhoc.txt", "lopsinhvien.txt", "loptinchi.txt"):
            (self.root / name).write_text("", encoding="utf-8")
        self.toast = patch("frontend.main_window.Notification.success")
        self.toast.start()
        self.window = MainWindow(data_dir=self.root)
        self.window.show()
        self.window.activateWindow()
        QTest.qWait(30)

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        QTest.qWait(20)
        self.toast.stop()
        self.temp.cleanup()

    def test_button_and_shortcut_refresh_pages_and_history(self):
        window = self.window
        self.assertFalse(window.undo_action.isEnabled())
        window.subject_manager.them_mon_hoc(MonHoc("MH1", "Mon mot", 3, 0))
        window.show_page("subject")
        self.assertTrue(window.undo_action.isEnabled())
        self.assertIn("MH1", window.undo_action.toolTip())
        button = window.subject_page.findChild(TopBar).undo_button
        QTest.mouseClick(button, Qt.MouseButton.LeftButton)
        self.assertEqual(window.subject_page.table.rowCount(), 0)
        self.assertFalse(window.undo_action.isEnabled())
        window.class_student_manager.them_lop(Lop("L1", "Lop mot"))
        window.show_page("student")
        window.class_student_page.open_student_list("L1")
        window.class_student_page.student_table.setFocus()
        QTest.keyClick(window.class_student_page.student_table, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
        self.assertIsNone(window.class_student_manager.tim_lop("L1"))
        self.assertIsNone(window.class_student_page.selected_class_code)
        self.assertEqual(window.class_student_page.content_stack.currentIndex(), 0)
        self.assertFalse(window.undo_action.isEnabled())

    def test_text_field_undo_keeps_saved_data_and_form_is_closed_after_data_undo(self):
        window = self.window
        window.subject_manager.them_mon_hoc(MonHoc("MH1", "Mon mot", 3, 0))
        window.show_page("subject")
        field = window.subject_page.search_input
        field.setFocus()
        QTest.keyClicks(field, "hello")
        QTest.keyClick(field, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
        self.assertEqual(field.text(), "")
        self.assertIsNotNone(window.subject_manager.tim_mon_hoc("MH1"))
        window.subject_page.edit_subject("MH1")
        QTest.qWait(250)
        window.undo_last_action()
        self.assertIsNone(window.subject_page.editor_host.form)
        self.assertIsNone(window.subject_manager.tim_mon_hoc("MH1"))

    def test_registration_selection_clears_when_student_is_undone(self):
        window = self.window
        window.class_student_manager.them_lop(Lop("L1", "Lop mot"))
        window.class_student_manager.them_sinh_vien("L1", SinhVien("SV1", "Nguyen", "An", "Nam", "0901234567"))
        window.show_page("registration")
        page = window.registration_page
        page.student_input.setText("SV1")
        page.find_student()
        self.assertIsNotNone(page.current_student)
        window.undo_last_action()
        self.assertIsNone(page.current_student)
        self.assertEqual(page.available_table.rowCount(), 0)
        self.assertEqual(page.registered_table.rowCount(), 0)

    def test_registration_button_updates_undo_and_save_error_allows_retry(self):
        window = self.window
        window.subject_manager.them_mon_hoc(MonHoc("MH1", "Mon mot", 3, 0))
        window.class_student_manager.them_lop(Lop("L1", "Lop mot"))
        window.class_student_manager.them_sinh_vien("L1", SinhVien("SV1", "Nguyen", "An", "Nam", "0901234567"))
        window.credit_class_manager.them_lop_tin_chi(LopTinChi("MH1", "2026-2027", 1, 1, 1, 10))
        window.app_data.clear_undo()
        window.show_page("registration")
        page = window.registration_page
        page.student_input.setText("SV1")
        page.find_student()
        page.selected_credit_class_id = 1
        with patch("frontend.pages.registration_page.ConfirmDialog.ask", return_value=True):
            page.register_selected()
        self.assertTrue(window.undo_action.isEnabled())
        self.assertEqual(window.app_data.so_thao_tac_undo, 1)
        self.assertEqual(page.registered_table.rowCount(), 1)
        blocker = self.root / "loptinchi.txt.tmp"
        blocker.mkdir()
        with patch("frontend.main_window.Notification.error") as error:
            window.undo_last_action()
            error.assert_called_once()
        self.assertTrue(window.undo_action.isEnabled())
        self.assertEqual(page.registered_table.rowCount(), 1)
        self.assertEqual(window.credit_class_page._source_credit_classes[0].so_sv_dang_ky, 1)
        blocker.rmdir()
        window.undo_last_action()
        self.assertFalse(window.undo_action.isEnabled())
        self.assertEqual(page.registered_table.rowCount(), 0)


if __name__ == "__main__":
    unittest.main()
