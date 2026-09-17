"""Trang đăng nhập PTIT và giao diện dùng chung cho trang đăng ký."""

from pathlib import Path
import sys

# Cho phép chạy trực tiếp file này ngoài package.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from PyQt6.QtCore import QByteArray, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from frontend.components.notification import NotificationBanner, NotificationType


_NAVY = "#0b234b"
_MUTED = "#7489ae"
_ICONS = {
    "user": '<circle cx="12" cy="7" r="4"/><path d="M4 22v-3a8 8 0 0 1 16 0v3z"/>',
    "users": '<circle cx="12" cy="6" r="4"/><circle cx="4" cy="9" r="3"/><circle cx="20" cy="9" r="3"/><path d="M5 22v-4a7 7 0 0 1 14 0v4zM0 19v-3a5 5 0 0 1 5-5l2 1a9 9 0 0 0-4 7zM24 19v-3a5 5 0 0 0-5-5l-2 1a9 9 0 0 1 4 7z"/>',
    "lock": '<path d="M6 10V7a6 6 0 0 1 12 0v3h-3V7a3 3 0 0 0-6 0v3z"/><rect x="3" y="10" width="18" height="13" rx="3"/><path d="M12 15v4" stroke="white" stroke-width="2"/>',
    "eye": '<path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" fill="none" stroke="currentColor" stroke-width="2.3"/><circle cx="12" cy="12" r="4"/>',
    "eye_off": '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12zM3 3l18 18" fill="none" stroke="currentColor" stroke-width="2.3"/>',
    "book": '<path d="M1 3c4-2 8-1 10 1v18c-3-2-6-3-10-1zM23 3c-4-2-8-1-10 1v18c3-2 6-3 10-1z"/>',
    "file": '<path d="M4 1h10l6 6v16H4z"/><path d="M14 1v7h6M8 13h8M8 18h8" fill="none" stroke="white" stroke-width="1.5"/>',
    "chart": '<rect x="2" y="14" width="5" height="9" rx="2"/><rect x="9" y="8" width="5" height="15" rx="2"/><rect x="16" y="1" width="5" height="22" rx="2"/>',
    "login": '<path d="M10 4V2h11v20H10v-3M2 12h12m-5-5 5 5-5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
}


def _icon(name, color, size=32):
    """Vẽ biểu tượng SVG sắc nét mà không phụ thuộc font emoji."""
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        f'fill="{color}" color="{color}">{_ICONS[name]}</svg>'
    )
    pixmap = QPixmap(size * 2, size * 2)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    QSvgRenderer(QByteArray(svg.encode())).render(painter)
    painter.end()
    pixmap.setDevicePixelRatio(2)
    return pixmap


class LoginPage(QWidget):
    """Trang đăng nhập có ảnh PTIT và form co giãn theo cửa sổ."""

    login_success = pyqtSignal(dict)
    register_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._custom_authenticator = None
        self._background = QPixmap(self._get_asset_path("ptit_background.png"))
        self._logo = QPixmap(self._get_asset_path("ptit_logo.png"))
        if not self._logo.isNull():
            # Ảnh logo nguồn có lề trắng lớn; chỉ crop khi hiển thị.
            width, height = self._logo.width(), self._logo.height()
            self._logo = self._logo.copy(
                round(width * 0.312),
                round(height * 0.235),
                round(width * 0.372),
                round(height * 0.468),
            )
            self._logo.setMask(
                self._logo.createMaskFromColor(QColor("white"), Qt.MaskMode.MaskInColor)
            )

        self._feature_icons = [
            _icon(name, color)
            for name, color in (
                ("users", "#1683ff"),
                ("book", "#00bea5"),
                ("file", "#ff9800"),
                ("chart", "#7935ff"),
            )
        ]
        self.setObjectName("loginPage")
        self.setWindowTitle("Hệ thống quản lý tín chỉ sinh viên")
        self.setWindowIcon(QIcon(self._logo))
        self.setMinimumSize(1000, 640)
        self.resize(1366, 875)
        self.init_ui()

    def init_ui(self):
        self.card = QFrame(self)
        self.card.setObjectName("loginCard")

        self.title_label = QLabel("Đăng nhập", self.card)
        self.subtitle_label = QLabel("Vui lòng đăng nhập để tiếp tục", self.card)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Giữ role_combo để tương thích với hàm xác thực hiện tại; giao diện
        # tham chiếu không hiển thị bộ chọn vai trò.
        self.role_combo = QComboBox(self)
        self.role_combo.addItems(
            [
                "Quản trị viên (Admin)",
                "Giảng viên (Teacher)",
                "Sinh viên (Student)",
            ]
        )
        self.role_combo.hide()

        self.username_input = QLineEdit(self.card)
        self.username_input.setPlaceholderText("Tên đăng nhập")
        self.username_input.setAccessibleName("Tên đăng nhập")
        self.password_input = QLineEdit(self.card)
        self.password_input.setPlaceholderText("Mật khẩu")
        self.password_input.setAccessibleName("Mật khẩu")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self._field_icons = []
        for field, icon_name in (
            (self.username_input, "user"),
            (self.password_input, "lock"),
        ):
            icon_label = QLabel(field)
            icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self._field_icons.append((icon_label, icon_name))
            field.returnPressed.connect(self.handle_login)
            field.textChanged.connect(self._on_input_changed)

        self.toggle_pass_btn = QPushButton(self.password_input)
        self.toggle_pass_btn.setObjectName("togglePassword")
        self.toggle_pass_btn.setCheckable(True)
        self.toggle_pass_btn.clicked.connect(self.toggle_password_visibility)
        self._update_password_button()

        self.login_btn = QPushButton("  Đăng nhập", self.card)
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setIcon(QIcon(_icon("login", "white")))
        self.login_btn.clicked.connect(self.handle_login)

        self.divider_label = QLabel("hoặc", self.card)
        self.divider_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.divider_left = QFrame(self.card)
        self.divider_right = QFrame(self.card)

        self.demo_btn = QPushButton(self.card)
        self.demo_btn.setObjectName("demoBtn")
        self.demo_btn.setAccessibleName("Đăng nhập với tài khoản demo")
        self.demo_btn.clicked.connect(self.handle_demo_login)
        self.demo_icon = QLabel(self.demo_btn)
        self.demo_title = QLabel("Đăng nhập với tài khoản demo", self.demo_btn)
        self.demo_subtitle = QLabel(
            "(Dành cho giảng viên / quản trị viên)", self.demo_btn
        )
        for label in (self.demo_icon, self.demo_title, self.demo_subtitle):
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.demo_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.demo_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.register_prompt = QLabel("Chưa có tài khoản?", self.card)
        self.register_prompt.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.register_btn = QPushButton("Đăng ký", self.card)
        self.register_btn.setObjectName("registerBtn")
        self.register_btn.setAccessibleName("Mở trang đăng ký tài khoản")
        self.register_btn.clicked.connect(self.register_clicked.emit)

        self.quote_label = QLabel(
            '"Tri thức là sức mạnh, quản lý là nền tảng\ncho tương lai."', self.card
        )
        self.quote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quote_author = QLabel("— PTIT —", self.card)
        self.quote_author.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.error_banner = NotificationBanner(dismissible=True, parent=self.card)
        self.error_banner.close_btn.clicked.connect(self._on_input_changed)

        for button in (
            self.toggle_pass_btn,
            self.login_btn,
            self.demo_btn,
            self.register_btn,
        ):
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        controls = [
            self.username_input,
            self.password_input,
            self.toggle_pass_btn,
            self.login_btn,
            self.demo_btn,
            self.register_btn,
        ]
        for first, second in zip(controls, controls[1:]):
            QWidget.setTabOrder(first, second)

        self._layout_screen()

    def _get_asset_path(self, filename):
        image_dir = Path(__file__).resolve().parent.parent / "resources" / "images"
        return str(image_dir / filename)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "card"):
            self._layout_screen()

    def _layout_screen(self):
        """Đặt vị trí widget theo khung tham chiếu 1536 x 984."""
        scale_x = self.width() / 1536
        scale_y = self.height() / 984
        scale = min(scale_x, scale_y)

        def place(widget, x, y, width, height):
            widget.setGeometry(
                round(x * scale_x),
                round(y * scale_y),
                round(width * scale_x),
                round(height * scale_y),
            )

        def style_label(label, size, color=_NAVY, weight=400, italic=False):
            label.setStyleSheet(
                "background: transparent; border: none; padding: 0;"
                f"color: {color}; font-family: 'Segoe UI';"
                f"font-size: {round(size * scale)}px; font-weight: {weight};"
                f"font-style: {'italic' if italic else 'normal'};"
            )

        self.setStyleSheet(
            f"""
            QWidget#loginPage, QWidget#registerPage {{
                font-family: 'Segoe UI'; color: {_NAVY};
            }}
            QLineEdit, QPushButton {{ font-family: 'Segoe UI'; }}
            QFrame#loginCard {{
                background: rgba(255, 255, 255, 245);
                border: 1px solid #e0ebfa;
                border-radius: {round(18 * scale)}px;
            }}
            QLineEdit {{
                background: transparent; color: {_NAVY};
                border: 1px solid #cfdcf1;
                border-radius: {round(12 * scale)}px;
                padding: 0;
                font-size: {round(21 * scale)}px;
                selection-background-color: #2984ff;
            }}
            QLineEdit:hover {{ border-color: #98b9e6; }}
            QLineEdit:focus {{ border: 2px solid #2984ff; }}
            QPushButton {{
                min-width: 0; min-height: 0; padding: 0;
                border: none; background: transparent;
            }}
            QPushButton#loginBtn {{
                background: #2d83f5; color: white;
                border-radius: {round(11 * scale)}px;
                font-size: {round(25 * scale)}px; font-weight: 600;
            }}
            QPushButton#loginBtn:hover {{ background: #1874eb; }}
            QPushButton#loginBtn:pressed {{ background: #1163cb; }}
            QPushButton#loginBtn:disabled {{ background: #94b9e9; }}
            QPushButton#demoBtn {{
                background: #f5f8fd; border: 1px solid #c8d9f2;
                border-radius: {round(13 * scale)}px;
            }}
            QPushButton#demoBtn:hover {{
                background: #eaf2ff; border-color: #8eb9f3;
            }}
            QPushButton#demoBtn:pressed {{ background: #dceaff; }}
            QPushButton#registerBtn {{
                color: #1680ff; font-size: {round(18 * scale)}px;
                font-weight: 600; text-align: left;
            }}
            QPushButton#registerBtn:hover {{
                color: #075bbf; text-decoration: underline;
            }}
            QPushButton:focus {{ border: 2px solid #7aaff4; }}
            QPushButton#togglePassword:hover {{
                background: #edf4ff; border-radius: {round(8 * scale)}px;
            }}
            """
        )

        place(self.card, 935, 54, 570, 832)
        place(self.title_label, 42, 62, 486, 57)
        place(self.subtitle_label, 42, 121, 486, 38)
        style_label(self.title_label, 40, weight=700)
        style_label(self.subtitle_label, 23, _MUTED)

        place(self.username_input, 43, 190, 486, 66)
        place(self.password_input, 43, 275, 486, 66)
        for field in (self.username_input, self.password_input):
            field.setTextMargins(round(63 * scale_x), 0, round(54 * scale_x), 0)
        for icon_label, icon_name in self._field_icons:
            place(icon_label, 21, 20, 26, 27)
            icon_label.setPixmap(
                _icon(icon_name, "#8d9ebc", max(16, round(26 * scale)))
            )
            icon_label.setStyleSheet(
                "background: transparent; border: none; padding: 0;"
            )

        place(self.toggle_pass_btn, 425, 9, 49, 48)
        self.toggle_pass_btn.setIconSize(QSize(round(27 * scale), round(27 * scale)))
        place(self.login_btn, 43, 375, 486, 66)
        self.login_btn.setIconSize(QSize(round(26 * scale), round(26 * scale)))

        place(self.divider_left, 43, 485, 201, 1)
        place(self.divider_right, 327, 485, 202, 1)
        for line in (self.divider_left, self.divider_right):
            line.setStyleSheet("background: #cbd9ee; border: none;")
        place(self.divider_label, 247, 465, 77, 38)
        style_label(self.divider_label, 21, _MUTED)

        place(self.demo_btn, 43, 520, 486, 76)
        place(self.demo_icon, 70, 24, 31, 29)
        self.demo_icon.setPixmap(_icon("users", _NAVY, round(30 * scale)))
        self.demo_icon.setStyleSheet(
            "background: transparent; border: none; padding: 0;"
        )
        place(self.demo_title, 108, 9, 345, 30)
        place(self.demo_subtitle, 108, 39, 345, 26)
        style_label(self.demo_title, 21, weight=500)
        style_label(self.demo_subtitle, 18, _MUTED)

        place(self.register_prompt, 120, 610, 220, 35)
        place(self.register_btn, 350, 610, 100, 35)
        style_label(self.register_prompt, 18, _MUTED)
        place(self.quote_label, 42, 677, 486, 65)
        place(self.quote_author, 42, 743, 486, 28)
        style_label(self.quote_label, 18, _MUTED, italic=True)
        style_label(self.quote_author, 19, _MUTED)
        place(self.error_banner, 43, 673, 486, 96)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        painter.scale(self.width() / 1536, self.height() / 984)
        painter.fillRect(QRectF(0, 0, 1536, 984), QColor("#f1f7ff"))

        if not self._background.isNull():
            ratio = max(
                1536 / self._background.width(),
                984 / self._background.height(),
            )
            painter.drawPixmap(
                QRectF(
                    0,
                    0,
                    self._background.width() * ratio,
                    self._background.height() * ratio,
                ),
                self._background,
                QRectF(self._background.rect()),
            )

        # Làm sáng phần chữ bên trái và che chữ có sẵn trong ảnh nền.
        veil = QLinearGradient(0, 0, 760, 0)
        veil.setColorAt(0, QColor(239, 247, 255, 255))
        veil.setColorAt(0.62, QColor(239, 247, 255, 255))
        veil.setColorAt(1, QColor(239, 247, 255, 0))
        overlay = QPixmap(950, 984)
        overlay.fill(Qt.GlobalColor.transparent)
        overlay_painter = QPainter(overlay)
        overlay_painter.fillRect(overlay.rect(), veil)
        vertical_fade = QLinearGradient(0, 0, 0, 984)
        vertical_fade.setColorAt(0, QColor(0, 0, 0, 40))
        vertical_fade.setColorAt(0.08, QColor(0, 0, 0, 255))
        vertical_fade.setColorAt(0.60, QColor(0, 0, 0, 255))
        vertical_fade.setColorAt(0.79, QColor(0, 0, 0, 50))
        vertical_fade.setColorAt(1, QColor(0, 0, 0, 10))
        overlay_painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_DestinationIn
        )
        overlay_painter.fillRect(overlay.rect(), vertical_fade)
        overlay_painter.end()
        painter.drawPixmap(0, 0, overlay)

        # Đường cong phân chia ảnh và khu vực form.
        wave = QPainterPath()
        wave.moveTo(950, 0)
        wave.cubicTo(785, 170, 1030, 395, 885, 718)
        wave.cubicTo(855, 805, 791, 930, 835, 984)
        wave.lineTo(1536, 984)
        wave.lineTo(1536, 0)
        wave.closeSubpath()
        painter.fillPath(wave, QColor("#f1f7ff"))

        def draw_text(
            x,
            y,
            width,
            height,
            value,
            size,
            color=_NAVY,
            bold=False,
            italic=False,
            family="Segoe UI",
        ):
            font = QFont(family)
            font.setPixelSize(size)
            font.setBold(bold)
            font.setItalic(italic)
            painter.setFont(font)
            painter.setPen(QColor(color))
            painter.drawText(
                QRectF(x, y, width, height),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                value,
            )

        if not self._logo.isNull():
            painter.drawPixmap(
                QRectF(83, 43, 116, 138), self._logo, QRectF(self._logo.rect())
            )
        else:
            draw_text(83, 65, 140, 90, "PTIT", 44, "#e51f24", True)

        draw_text(
            233,
            78,
            325,
            88,
            "HỌC VIỆN\nCÔNG NGHỆ BƯU CHÍNH\nVIỄN THÔNG",
            21,
            bold=True,
        )
        painter.fillRect(QRectF(233, 175, 52, 2), QColor("#ff323b"))
        draw_text(79, 222, 570, 114, "Hệ thống quản lý\ntín chỉ sinh viên", 47, bold=True)
        draw_text(
            79,
            342,
            540,
            66,
            "Quản lý sinh viên, môn học, đăng ký học\nvà điểm số một cách hiệu quả",
            23,
            _MUTED,
        )

        features = [
            ("Quản lý sinh viên", "#bedfff"),
            ("Quản lý môn học", "#bef0e6"),
            ("Đăng ký học & lớp tín chỉ", "#fbe2bd"),
            ("Thống kê & báo cáo", "#dad0ff"),
        ]
        for index, (caption, color) in enumerate(features):
            y = 430 + index * 63
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(color))
            painter.drawEllipse(QRectF(79, y, 54, 54))
            painter.drawPixmap(
                QRectF(91, y + 12, 30, 30),
                self._feature_icons[index],
                QRectF(self._feature_icons[index].rect()),
            )
            draw_text(155, y, 400, 54, caption, 21)

        draw_text(
            51, 807, 410, 64, "Tri thức", 49, "white", italic=True, family="Segoe Script"
        )
        draw_text(
            78,
            866,
            445,
            64,
            "Kết nối tương lai",
            39,
            "white",
            italic=True,
            family="Segoe Script",
        )
        painter.setPen(QPen(QColor("#fa3439"), 4))
        painter.drawLine(155, 932, 335, 907)
        draw_text(1445, 922, 75, 38, "v1.0.0", 20, _MUTED)
        painter.end()

    def _update_password_button(self):
        visible = self.password_input.echoMode() == QLineEdit.EchoMode.Normal
        self.toggle_pass_btn.setChecked(visible)
        self.toggle_pass_btn.setIcon(
            QIcon(_icon("eye_off" if visible else "eye", "#8d9ebc"))
        )
        label = "Ẩn mật khẩu" if visible else "Hiện mật khẩu"
        self.toggle_pass_btn.setToolTip(label)
        self.toggle_pass_btn.setAccessibleName(label)

    def toggle_password_visibility(self):
        visible = self.password_input.echoMode() == QLineEdit.EchoMode.Password
        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
        )
        self._update_password_button()

    def _on_input_changed(self):
        self.error_banner.hide()
        self.quote_label.show()
        self.quote_author.show()

    def set_authenticator(self, auth_func):
        """Nhận hàm (username, password, role) -> (thành công, dữ liệu/lỗi)."""
        self._custom_authenticator = auth_func

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        role = self.role_combo.currentText()

        if not username:
            self.show_error("Vui lòng nhập tên đăng nhập hoặc mã sinh viên!")
            self.username_input.setFocus()
            return
        if not password:
            self.show_error("Vui lòng nhập mật khẩu!")
            self.password_input.setFocus()
            return

        if self._custom_authenticator:
            try:
                success, result = self._custom_authenticator(username, password, role)
            except Exception:
                self.show_error("Không thể kết nối hệ thống. Vui lòng thử lại sau.")
                return
            if not success:
                self.show_error(
                    str(result)
                    if result
                    else "Tên đăng nhập hoặc mật khẩu không chính xác!"
                )
                return
            user_info = (
                dict(result)
                if isinstance(result, dict)
                else {"username": username, "role": role}
            )
            user_info.setdefault("remember", False)
        else:
            # Chế độ chạy riêng trang: giữ tài khoản demo admin/admin.
            if username.casefold() == "admin" and password != "admin":
                self.show_error("Tên đăng nhập hoặc mật khẩu không chính xác!")
                return
            user_info = {
                "username": username,
                "role": role,
                "remember": False,
            }

        self._on_input_changed()
        self.login_success.emit(user_info)

    def handle_demo_login(self):
        self.username_input.setText("admin")
        self.password_input.setText("admin")
        self.role_combo.setCurrentIndex(0)
        self.handle_login()

    def show_error(self, message):
        self.quote_label.hide()
        self.quote_author.hide()
        self.error_banner.message_label.setTextFormat(Qt.TextFormat.PlainText)
        self.error_banner.set_message(message, NotificationType.ERROR)

    def clear(self):
        self.username_input.clear()
        self.password_input.clear()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._update_password_button()
        self._on_input_changed()
        self.username_input.setFocus()


if __name__ == "__main__":
    from frontend.main_window import MainWindow

    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    raise SystemExit(application.exec())
