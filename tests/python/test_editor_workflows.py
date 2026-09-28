"""Behavior checks for non-modal forms, filtering and registration identity."""
import os
from pathlib import Path
import unittest
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PyQt6.QtCore import QAbstractAnimation, Qt
from PyQt6.QtGui import QFontDatabase, QValidator
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QDialogButtonBox

from bridge import (AppData, Lop, SinhVien, MonHoc, LopTinChi,
                    MonHocManager, LopSinhVienManager, LopTinChiManager)
from frontend.pages.subject_page import SubjectPage
from frontend.pages.class_student_page import ClassStudentPage
from frontend.pages.credit_class_page import CreditClassPage, current_academic_year
from frontend.pages.registration_page import AvailableClassTable, RegisteredClassTable


class EditorWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        for font in ('segoeui.ttf', 'segoeuib.ttf'):
            path = Path('C:/Windows/Fonts') / font
            if path.exists():
                QFontDatabase.addApplicationFont(str(path))
        resources = Path(__file__).resolve().parents[2] / 'frontend/resources'
        style = (resources / 'styles/ptit.qss').read_text(encoding='utf-8')
        for token, icon in [('__CHEVRON_DOWN_ICON__', 'chevron_down.svg'),
                            ('__CHEVRON_UP_ICON__', 'chevron_up.svg')]:
            style = style.replace(token, (resources / 'icons' / icon).as_posix())
        cls.app.setStyleSheet(style)

    def setUp(self):
        # In-memory managers never read/write the user's data files.
        self.data = AppData()
        self.subjects = MonHocManager(self.data)
        self.students = LopSinhVienManager(self.data)
        self.credits = LopTinChiManager(self.data)
        self.subjects.them_mon_hoc(MonHoc('MH1', 'Mon mot', 3, 0))
        self.students.them_lop(Lop('L1', 'Lop mot'))
        self.pages = []
        self.toast = patch('frontend.components.notification.Notification.success')
        self.toast.start()

    def tearDown(self):
        for page in self.pages:
            page.close()
            page.deleteLater()
        QTest.qWait(20)
        self.toast.stop()

    def show_page(self, page):
        self.pages.append(page)
        page.resize(1536, 900)
        page.show()
        QTest.qWait(20)
        return page

    def form(self, page):
        QTest.qWait(260)
        form = page.editor_host.form
        self.assertIsNotNone(form)
        self.assertFalse(form.isWindow())
        self.assertIsNone(QApplication.activeModalWidget())
        return form

    def save(self, form):
        host = form.window().editor_host
        button = form.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Save)
        QTest.mouseClick(button, Qt.MouseButton.LeftButton)
        for _ in range(100):
            QTest.qWait(10)
            if host.animation.state() == QAbstractAnimation.State.Stopped:
                break

    def test_subject_add_edit_and_duplicate(self):
        page = self.show_page(SubjectPage(self.subjects, MonHoc))
        page.add_subject()
        form = self.form(page)
        form.code_input.setText('MH2')
        form.name_input.setText('Mon hai')
        self.save(form)
        self.assertEqual(self.subjects.tim_mon_hoc('MH2').ten_mh, 'Mon hai')
        self.assertIs(page.editor_host.form, form)  # Repeated entry stays available.
        form.code_input.setText('MH2')
        form.name_input.setText('Trung ma')
        self.save(form)
        self.assertTrue(form.code_input.property('invalid'))
        self.assertEqual(self.subjects.tong_so_mon_hoc(), 2)
        page.edit_subject('MH2')
        form = self.form(page)
        self.assertTrue(form.code_input.isReadOnly())
        form.name_input.setText('Mon hai moi')
        self.save(form)
        self.assertEqual(self.subjects.tim_mon_hoc('MH2').ten_mh, 'Mon hai moi')
        self.assertIsNone(page.editor_host.form)

    def test_class_and_student_add_edit(self):
        page = self.show_page(ClassStudentPage(self.students, Lop, SinhVien))
        page.add_class()
        form = self.form(page)
        form.code_input.setText('L2')
        form.name_input.setText('Lop hai')
        self.save(form)
        page.edit_class('L2')
        form = self.form(page)
        form.name_input.setText('Lop hai moi')
        self.save(form)
        self.assertEqual(self.students.tim_lop('L2').ten_lop, 'Lop hai moi')
        page.open_student_list('L2')
        page.add_student()
        form = self.form(page)
        for field, value in [(form.code_input, 'SV2'), (form.surname_input, 'Nguyen'),
                             (form.given_name_input, 'An'), (form.phone_input, '0901234567')]:
            field.setText(value)
        self.save(form)
        self.assertEqual(self.students.tim_sinh_vien('SV2').ten, 'An')
        page.edit_student('SV2')
        form = self.form(page)
        form.given_name_input.setText('Binh')
        self.save(form)
        self.assertEqual(self.students.tim_sinh_vien('SV2').ten, 'Binh')
        self.assertIsNone(page.editor_host.form)

    def test_credit_add_edit_and_combined_filters(self):
        page = self.show_page(CreditClassPage(self.credits, LopTinChi, self.subjects))
        page.add_credit_class()
        form = self.form(page)
        form.subject_input.setCurrentText('MH1')
        form.year_input.setText(current_academic_year())
        form.group_input.setValue(2)
        self.save(form)
        item = list(self.credits.lay_danh_sach_lop_tin_chi())[0]
        page.edit_credit_class(item.ma_lop_tc)
        form = self.form(page)
        form.maximum_input.setValue(55)
        self.save(form)
        self.assertEqual(self.credits.tim_lop_tin_chi(item.ma_lop_tc).so_sv_max, 55)
        self.credits.them_lop_tin_chi(LopTinChi('MH1', current_academic_year(), 2, 3, 20, 50))
        page.refresh()
        page.year_filter.setCurrentIndex(page.year_filter.findData(current_academic_year()))
        page.group_filter.setCurrentIndex(page.group_filter.findData(2))
        page.semester_filter.setCurrentIndex(page.semester_filter.findData(1))
        page.search_input.setText('Mon mot')
        self.assertEqual(page.table.rowCount(), 1)
        self.assertEqual(page.table.item(0, 3).text(), 'Mon mot')
        page.semester_filter.setCurrentIndex(page.semester_filter.findData(2))
        self.assertEqual(page.table.rowCount(), 0)
        page.refresh()
        self.assertEqual(page.group_filter.currentData(), 2)

    def test_failed_edit_keeps_form_and_values(self):
        page = self.show_page(SubjectPage(self.subjects, MonHoc))
        page.edit_subject('MH1')
        form = self.form(page)
        form.name_input.setText('Ten moi')
        # Simulate a backend failure after frontend validation succeeds.
        with patch.object(page, '_new_subject', side_effect=ValueError('Khong the luu')):
            self.save(form)
        self.assertIs(page.editor_host.form, form)
        self.assertEqual(form.name_input.text(), 'Ten moi')
        self.assertEqual(form.status_label.text(), 'Khong the luu')
        self.assertEqual(self.subjects.tim_mon_hoc('MH1').ten_mh, 'Mon mot')
        form.reject()
        QTest.qWait(270)
        self.assertIsNone(page.editor_host.form)

    def test_required_fields_and_input_rules_survive_panel(self):
        page = self.show_page(SubjectPage(self.subjects, MonHoc))
        page.add_subject()
        form = self.form(page)
        self.save(form)
        self.assertTrue(form.code_input.property('invalid'))
        self.assertTrue(form.name_input.property('invalid'))
        self.assertEqual(form.code_input.maxLength(), 10)
        validator = form.code_input.validator()
        self.assertEqual(validator.validate(' A', 2)[0], QValidator.State.Invalid)
        self.assertEqual(validator.validate('A  B', 4)[0], QValidator.State.Invalid)
        form.code_input.setText('MH@')
        form.name_input.setText('Ten hop le')
        self.save(form)
        self.assertTrue(form.code_input.property('invalid'))
        # Closing before error timers expire must safely destroy the form.
        page.editor_host.close_panel(immediate=True)
        QTest.qWait(1600)
        self.assertEqual(self.subjects.tong_so_mon_hoc(), 1)

    def test_panel_resize_escape_and_navigation(self):
        page = self.show_page(ClassStudentPage(self.students, Lop, SinhVien))
        page.add_class()
        form = self.form(page)
        host = page.editor_host
        self.assertFalse(host.overlay)
        self.assertEqual(host.content.width() + host.panel.width(), host.width())
        page.resize(1050, 680)
        QTest.qWait(50)
        self.assertTrue(host.overlay)
        self.assertEqual(host.content.width(), host.width())
        self.assertEqual(host.panel.geometry().right(), host.width() - 1)
        QTest.keyClick(form.code_input, Qt.Key.Key_Escape)
        QTest.qWait(270)
        self.assertIsNone(host.form)
        page.open_student_list('L1')
        page.add_student()
        self.form(page)
        page.show_class_list()
        self.assertIsNone(host.form)
        page.add_class()
        self.form(page)
        page.hide()
        self.assertIsNone(host.form)

    def test_hidden_registration_id_still_selects_correct_class(self):
        self.credits.them_lop_tin_chi(LopTinChi('MH1', current_academic_year(), 1, 1, 20, 50))
        item = list(self.credits.lay_danh_sach_lop_tin_chi())[0]
        registered = RegisteredClassTable()
        available = AvailableClassTable()
        self.pages.extend([registered, available])
        registered.set_classes([item], {'MH1': 'Mon mot'})
        registered.selectRow(0)
        self.assertEqual(registered.selected_class_id(), item.ma_lop_tc)
        self.assertEqual(registered.item(0, 0).text(), 'MH1')
        self.assertEqual(registered.columnCount(), 4)
        available.set_classes([item], {'MH1': 'Mon mot'}, set())
        chosen = []
        available.selection_changed.connect(chosen.append)
        available.button_group.buttons()[0].setChecked(True)
        self.assertEqual(chosen, [item.ma_lop_tc])
        self.assertEqual(available.item(0, 1).text(), 'MH1')
        self.assertEqual(available.columnCount(), 7)
        available.set_classes([item], {'MH1': 'Mon mot'}, {'MH1'}, {item.ma_lop_tc})
        self.assertFalse(available.button_group.buttons()[0].isEnabled())


if __name__ == '__main__':
    unittest.main()
