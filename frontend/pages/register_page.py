"""Trang đăng ký tài khoản cho hệ thống quản lý tín chỉ PTIT."""

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget

from frontend.pages.login_page import LoginPage, _MUTED, _NAVY, _icon


class RegisterPage(LoginPage):
    """Form đăng ký dùng chung nền và nhận diện thương hiệu với trang đăng nhập."""

    registration_submitted = pyqtSignal(dict)
    back_to_login_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("registerPage")
        self.setWindowTitle("Đăng ký tài khoản - Hệ thống quản lý tín chỉ sinh viên")
        self._build_register_form()
        self._layout_screen()

    def _build_register_form(self):
        for widget in (
            self.username_input, self.password_input, self.toggle_pass_btn,
            self.login_btn, self.divider_label, self.divider_left,
            self.divider_right, self.demo_btn, self.register_prompt,
            self.register_btn,
        ):
            widget.hide()

        self.title_label.setText("Đăng ký")
        self.subtitle_label.setText("Tạo tài khoản sinh viên mới")

        self.back_btn = QPushButton("‹  Quay lại trang đăng nhập", self.card)
        self.back_btn.setObjectName("backToLoginBtn")
        self.back_btn.setAccessibleName("Quay lại trang đăng nhập")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_to_login_clicked.emit)

        fields = [
            ("full_name_input", "Họ và tên", "user", False),
            ("register_username_input", "Tên đăng nhập / Mã sinh viên", "user", False),
            ("register_password_input", "Mật khẩu", "lock", True),
            ("confirm_password_input", "Nhập lại mật khẩu", "lock", True),
        ]
        self._register_fields = []
        self._register_field_icons = []
        for attr, placeholder, icon_name, password in fields:
            field = QLineEdit(self.card)
            field.setPlaceholderText(placeholder)
            field.setAccessibleName(placeholder)
            if password:
                field.setEchoMode(QLineEdit.EchoMode.Password)
            field.textChanged.connect(self._on_input_changed)
            field.returnPressed.connect(self.handle_register)
            setattr(self, attr, field)
            self._register_fields.append(field)
            icon = QLabel(field)
            icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self._register_field_icons.append((icon, icon_name))

        self.password_toggle_btn = self._make_password_toggle(self.register_password_input)
        self.confirm_toggle_btn = self._make_password_toggle(self.confirm_password_input)

        self.submit_register_btn = QPushButton("Đăng ký", self.card)
        self.submit_register_btn.setObjectName("submitRegisterBtn")
        self.submit_register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_register_btn.clicked.connect(self.handle_register)

        controls = [self.back_btn, *self._register_fields,
                    self.password_toggle_btn, self.confirm_toggle_btn,
                    self.submit_register_btn]
        for first, second in zip(controls, controls[1:]):
            QWidget.setTabOrder(first, second)

    def _make_password_toggle(self, field):
        button = QPushButton(field)
        button.setObjectName("registerPasswordToggle")
        button.setCheckable(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(lambda _checked, f=field, b=button: self._toggle_password(f, b))
        self._update_toggle_icon(field, button)
        return button

    @staticmethod
    def _update_toggle_icon(field, button):
        visible = field.echoMode() == QLineEdit.EchoMode.Normal
        button.setChecked(visible)
        button.setIcon(QIcon(_icon("eye_off" if visible else "eye", "#8d9ebc")))
        label = "Ẩn mật khẩu" if visible else "Hiện mật khẩu"
        button.setToolTip(label)
        button.setAccessibleName(label)

    def _toggle_password(self, field, button):
        visible = field.echoMode() == QLineEdit.EchoMode.Password
        field.setEchoMode(QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password)
        self._update_toggle_icon(field, button)

    def _layout_screen(self):
        super()._layout_screen()
        if not hasattr(self, "_register_fields"):
            return

        sx, sy = self.width() / 1536, self.height() / 984
        scale = min(sx, sy)

        def place(widget, x, y, width, height):
            widget.setGeometry(round(x * sx), round(y * sy),
                               round(width * sx), round(height * sy))

        # LoginPage rebuilds its responsive stylesheet on each resize, so add
        # the registration-specific rules again after the shared rules.
        self.setStyleSheet(self.styleSheet() + f"""
            QPushButton#backToLoginBtn {{ color: #1680ff; font-size: {round(17 * scale)}px;
                font-weight: 500; text-align: left; }}
            QPushButton#backToLoginBtn:hover {{ color: #075bbf; text-decoration: underline; }}
            QPushButton#submitRegisterBtn {{ background: #2d83f5; color: white;
                border-radius: {round(11 * scale)}px; font-size: {round(23 * scale)}px;
                font-weight: 600; }}
            QPushButton#submitRegisterBtn:hover {{ background: #1874eb; }}
            QPushButton#submitRegisterBtn:pressed {{ background: #1163cb; }}
            QPushButton#registerPasswordToggle:hover {{ background: #edf4ff;
                border-radius: {round(8 * scale)}px; }}
        """)
        place(self.back_btn, 30, 22, 235, 34)
        place(self.title_label, 42, 55, 486, 54)
        place(self.subtitle_label, 42, 107, 486, 35)

        for index, field in enumerate(self._register_fields):
            place(field, 43, 158 + index * 78, 486, 60)
            right_margin = round(54 * sx) if field.echoMode() in (
                QLineEdit.EchoMode.Password, QLineEdit.EchoMode.Normal
            ) and field in (self.register_password_input, self.confirm_password_input) else round(18 * sx)
            field.setTextMargins(round(63 * sx), 0, right_margin, 0)
        for icon, name in self._register_field_icons:
            place(icon, 21, 17, 26, 27)
            icon.setPixmap(_icon(name, "#8d9ebc", max(16, round(26 * scale))))
            icon.setStyleSheet("background: transparent; border: none; padding: 0;")
        for button in (self.password_toggle_btn, self.confirm_toggle_btn):
            place(button, 425, 6, 49, 48)
            button.setIconSize(QSize(round(27 * scale), round(27 * scale)))

        place(self.submit_register_btn, 43, 490, 486, 64)
        place(self.quote_label, 42, 650, 486, 65)
        place(self.quote_author, 42, 716, 486, 28)
        place(self.error_banner, 43, 626, 486, 112)

    def handle_register(self):
        full_name = " ".join(self.full_name_input.text().split())
        username = self.register_username_input.text().strip()
        password = self.register_password_input.text()
        confirmation = self.confirm_password_input.text()

        if not full_name:
            self.show_error("Vui lòng nhập họ và tên!")
            self.full_name_input.setFocus()
            return
        if not username:
            self.show_error("Vui lòng nhập tên đăng nhập hoặc mã sinh viên!")
            self.register_username_input.setFocus()
            return
        if any(character.isspace() for character in username):
            self.show_error("Tên đăng nhập không được chứa khoảng trắng!")
            self.register_username_input.setFocus()
            return
        if len(password) < 6:
            self.show_error("Mật khẩu phải có ít nhất 6 ký tự!")
            self.register_password_input.setFocus()
            return
        if password != confirmation:
            self.show_error("Mật khẩu nhập lại không khớp!")
            self.confirm_password_input.setFocus()
            return

        self.registration_submitted.emit({
            "full_name": full_name,
            "username": username,
            "password": password,
            "role": "Sinh viên (Student)",
        })

    def clear(self):
        for field in self._register_fields:
            field.clear()
        for field, button in (
            (self.register_password_input, self.password_toggle_btn),
            (self.confirm_password_input, self.confirm_toggle_btn),
        ):
            field.setEchoMode(QLineEdit.EchoMode.Password)
            self._update_toggle_icon(field, button)
        self._on_input_changed()
        self.full_name_input.setFocus()
