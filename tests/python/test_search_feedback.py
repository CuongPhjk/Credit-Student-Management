"""Checks for search feedback without popup notifications."""
import os
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from frontend.components.inline_notice import InlineNotice
from frontend.pages.registration_page import RegistrationPage
from frontend.pages.score_page import ScorePage


class SearchFeedbackTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widgets = []
        # Patch where pages resolve the notification class.
        self.registration_popups = patch('frontend.pages.registration_page.Notification')
        self.score_popups = patch('frontend.pages.score_page.Notification')
        self.registration_notification = self.registration_popups.start()
        self.score_notification = self.score_popups.start()

    def tearDown(self):
        for widget in self.widgets:
            widget.close()
            widget.deleteLater()
        QTest.qWait(20)
        self.registration_popups.stop()
        self.score_popups.stop()

    def show(self, widget):
        self.widgets.append(widget)
        widget.resize(1536, 900)
        widget.show()
        QTest.qWait(30)
        return widget

    def test_empty_student_code_only_marks_input_then_clears_on_typing(self):
        manager = Mock()
        page = self.show(RegistrationPage(class_student_manager=manager))
        page.find_student()
        self.assertTrue(page.student_input.property('invalid'))
        self.assertTrue(page.student_notice.banner.isHidden())
        manager.tim_thong_tin_sinh_vien.assert_not_called()
        self.assertFalse(self.registration_notification.mock_calls)
        page.student_input.setText('SV1')
        self.assertFalse(page.student_input.property('invalid'))

    def test_missing_student_slides_in_and_clears_stale_student(self):
        student = SimpleNamespace(ma_sv='SV1', ho_ten='Nguyen An', phai='Nam', so_dt='0901234567')
        manager = Mock()
        manager.tim_thong_tin_sinh_vien.side_effect = [
            {'sinh_vien': student, 'ma_lop': 'L1'}, None,
        ]
        page = self.show(RegistrationPage(class_student_manager=manager))
        page.student_input.setText('SV1')
        page.find_student()
        self.assertIs(page.current_student, student)
        page.student_input.setText('UNKNOWN')
        page.find_student()
        self.assertEqual(page.student_notice.message.text(), 'Không tìm thấy sinh viên')
        start_x = page.student_notice.banner.x()
        QTest.qWait(260)
        self.assertLess(page.student_notice.banner.x(), start_x)
        self.assertIsNone(page.current_student)
        self.assertEqual(page.student_name_label.text(), 'Chưa chọn sinh viên')
        self.assertEqual(page.available_table.rowCount(), 0)
        self.assertFalse(page.student_input.property('invalid'))
        self.assertFalse(self.registration_notification.mock_calls)
        page.student_input.setText('SV2')
        self.assertTrue(page.student_notice.banner.isHidden())

    def test_empty_scores_use_inline_notice_and_success_clears_it(self):
        credits = Mock()
        credits.lay_danh_sach_lop_tin_chi.return_value = [SimpleNamespace(
            nien_khoa='2026-2027', hoc_ky=1, ma_mh='MH1', nhom=1, huy_lop=False,
        )]
        scores = Mock()
        scores.lay_danh_sach_sinh_vien.return_value = []
        page = self.show(ScorePage(scores, credits))
        page.load_students()
        self.assertEqual(page.empty_notice.message.text(), 'Không có dữ liệu')
        self.assertFalse(page.empty_notice.banner.isHidden())
        self.assertFalse(self.score_notification.mock_calls)
        for combo in (page.year_input, page.semester_input, page.subject_input, page.group_input):
            self.assertFalse(combo.property('invalid'))
        scores.lay_danh_sach_sinh_vien.return_value = [
            {'ma_sv': 'SV1', 'ho': 'Nguyen', 'ten': 'An', 'diem': 0, 'da_co_diem': False}
        ]
        page.load_students()
        self.assertTrue(page.empty_notice.banner.isHidden())
        self.assertEqual(page.table.rowCount(), 1)

    def test_show_open_classes_requires_student_code(self):
        page = self.show(RegistrationPage())
        with patch.object(page, '_load_tables') as load:
            page.load_term()
            self.assertEqual(page.student_notice.message.text(), 'Vui lòng nhập mã sinh viên')
            self.assertFalse(page.student_notice.banner.isHidden())
            load.assert_not_called()
            # Clearing a previously found code must still require entry.
            page.current_student = SimpleNamespace(ma_sv='SV1')
            page.load_term()
            load.assert_not_called()
            page.student_input.setText('SV1')
            page.load_term()
            load.assert_called_once()
        self.assertFalse(self.registration_notification.mock_calls)

    def test_register_without_data_or_selection_uses_inline_notice(self):
        manager = Mock()
        page = self.show(RegistrationPage(registration_manager=manager))
        with patch('frontend.pages.registration_page.ConfirmDialog.ask') as confirm:
            page.register_selected()
            self.assertEqual(page.registration_notice.message.text(), 'Vui lòng chọn lớp tín chỉ')
            self.assertFalse(page.registration_notice.banner.isHidden())
            page.current_student = SimpleNamespace(ma_sv='SV1')
            page.register_selected()
            self.assertFalse(page.registration_notice.banner.isHidden())
            confirm.assert_not_called()
            manager.dang_ky.assert_not_called()
            page._select_credit_class(1)
            self.assertTrue(page.registration_notice.banner.isHidden())
            confirm.return_value = True
            page.register_selected()
            manager.dang_ky.assert_called_once_with(1, 'SV1')
        self.registration_notification.warning.assert_not_called()

    def test_no_credit_classes_show_no_data_without_marking_combos(self):
        page = self.show(ScorePage())
        page.load_students()
        self.assertEqual(page.empty_notice.message.text(), 'Không có dữ liệu')
        self.assertFalse(page.empty_notice.banner.isHidden())
        self.assertFalse(self.score_notification.mock_calls)
        page.year_input.addItem('2026-2027', '2026-2027')
        self.assertTrue(page.empty_notice.banner.isHidden())

    def test_two_second_timeout_restarts_and_hiding_page_cancels(self):
        notice = self.show(InlineNotice())
        notice.show_message('Không có dữ liệu')
        QTest.qWait(1200)
        notice.show_message('Không tìm thấy sinh viên')
        QTest.qWait(1200)
        self.assertFalse(notice.banner.isHidden())
        QTest.qWait(1000)
        self.assertTrue(notice.banner.isHidden())
        notice.show_message('Không có dữ liệu')
        notice.hide()
        self.assertFalse(notice.timer.isActive())
        notice.show()
        self.assertTrue(notice.banner.isHidden())


if __name__ == '__main__':
    unittest.main()
