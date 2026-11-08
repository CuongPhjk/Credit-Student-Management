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


class SearchFeedbackTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widgets = []

    def tearDown(self):
        for widget in self.widgets:
            widget.close()
            widget.deleteLater()
        QTest.qWait(20)

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
        self.assertEqual(page.page_notice.message_label.text(), 'Vui lòng nhập mã sinh viên')
        self.assertFalse(page.page_notice.isHidden())
        manager.tim_thong_tin_sinh_vien.assert_not_called()
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
        self.assertEqual(page.page_notice.message_label.text(), 'Không tìm thấy sinh viên')
        self.assertFalse(page.page_notice.isHidden())
        self.assertIsNone(page.current_student)
        self.assertEqual(page.student_name_label.text(), 'Chưa chọn sinh viên')
        self.assertEqual(page.available_table.rowCount(), 0)
        self.assertFalse(page.student_input.property('invalid'))
        page.student_input.setText('SV2')
        self.assertTrue(page.page_notice.isHidden())

    def test_show_open_classes_requires_student_code(self):
        page = self.show(RegistrationPage())
        with patch.object(page, '_load_tables') as load:
            page.load_term()
            self.assertEqual(page.page_notice.message_label.text(), 'Vui lòng nhập mã sinh viên')
            self.assertFalse(page.page_notice.isHidden())
            load.assert_not_called()
            # Clearing a previously found code must still require entry.
            page.current_student = SimpleNamespace(ma_sv='SV1')
            page.load_term()
            load.assert_not_called()
            page.student_input.setText('SV1')
            page.load_term()
            load.assert_called_once()

    def test_register_without_data_or_selection_uses_inline_notice(self):
        manager = Mock()
        page = self.show(RegistrationPage(registration_manager=manager))
        with patch('frontend.pages.registration_page.ConfirmDialog.ask') as confirm:
            page.register_selected()
            self.assertEqual(page.page_notice.message_label.text(), 'Vui lòng chọn lớp tín chỉ')
            self.assertFalse(page.page_notice.isHidden())
            page.current_student = SimpleNamespace(ma_sv='SV1')
            page.register_selected()
            self.assertFalse(page.page_notice.isHidden())
            confirm.assert_not_called()
            manager.dang_ky.assert_not_called()
            page._select_credit_class(1)
            self.assertTrue(page.page_notice.isHidden())
            confirm.return_value = True
            page.register_selected()
            manager.dang_ky.assert_called_once_with(1, 'SV1')

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
