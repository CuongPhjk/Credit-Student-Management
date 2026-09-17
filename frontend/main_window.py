"""Cửa sổ ứng dụng và bộ điều hướng giữa đăng nhập, đăng ký."""

import hashlib
import hmac

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from frontend.components.notification import NotificationType
from frontend.pages import LoginPage, RegisterPage


class MainWindow(QMainWindow):
    """Điều phối luồng xác thực của ứng dụng."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hệ thống quản lý tín chỉ sinh viên")
        self.setMinimumSize(1000, 640)
        self.resize(1366, 875)

        self.login_page = LoginPage()
        self.register_page = RegisterPage()
        self.setWindowIcon(QIcon(self.login_page._logo))

        self.pages = QStackedWidget()
        self.pages.addWidget(self.login_page)
        self.pages.addWidget(self.register_page)
        self.setCentralWidget(self.pages)

        self._accounts = {
            "admin": {
                "username": "admin",
                "full_name": "Quản trị viên",
                "password_hash": self._hash_password("admin"),
                "role": "Quản trị viên (Admin)",
            }
        }
        self.login_page.set_authenticator(self._authenticate)
        self.login_page.register_clicked.connect(self.show_register)
        self.register_page.back_to_login_clicked.connect(self.show_login)
        self.register_page.registration_submitted.connect(self._register_account)
        self.show_login()

    @staticmethod
    def _hash_password(password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _authenticate(self, username, password, _selected_role):
        account = self._accounts.get(username.casefold())
        if account is None or not hmac.compare_digest(
            account["password_hash"], self._hash_password(password)
        ):
            return False, "Tên đăng nhập hoặc mật khẩu không chính xác!"
        return True, {
            "username": account["username"],
            "full_name": account["full_name"],
            "role": account["role"],
        }

    def _register_account(self, account):
        key = account["username"].casefold()
        if key in self._accounts:
            self.register_page.show_error("Tên đăng nhập này đã tồn tại!")
            self.register_page.register_username_input.setFocus()
            return

        self._accounts[key] = {
            "username": account["username"],
            "full_name": account["full_name"],
            "password_hash": self._hash_password(account["password"]),
            "role": account["role"],
        }
        self.login_page.clear()
        self.login_page.username_input.setText(account["username"])
        self.login_page.role_combo.setCurrentText(account["role"])
        self.pages.setCurrentWidget(self.login_page)
        self.login_page.quote_label.hide()
        self.login_page.quote_author.hide()
        self.login_page.error_banner.set_message(
            "Đăng ký thành công. Vui lòng nhập mật khẩu để đăng nhập.",
            NotificationType.SUCCESS,
        )
        self.login_page.password_input.setFocus()

    def show_register(self):
        self.login_page._on_input_changed()
        self.register_page.clear()
        self.pages.setCurrentWidget(self.register_page)

    def show_login(self):
        self.register_page._on_input_changed()
        self.pages.setCurrentWidget(self.login_page)
        self.login_page.username_input.setFocus()
