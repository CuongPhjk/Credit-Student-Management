from enum import Enum
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QGraphicsOpacityEffect,
)


class NotificationType(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


_TYPE_CONFIG = {
    NotificationType.SUCCESS: {
        "icon": "✓",
        "bg_color": "#ecfdf5",
        "border_color": "#a7f3d0",
        "icon_color": "#059669",
        "title_color": "#065f46",
        "text_color": "#047857",
        "default_title": "Thành công",
    },
    NotificationType.ERROR: {
        "icon": "✕",
        "bg_color": "#fef2f2",
        "border_color": "#fecaca",
        "icon_color": "#dc2626",
        "title_color": "#991b1b",
        "text_color": "#b91c1c",
        "default_title": "Lỗi",
    },
    NotificationType.WARNING: {
        "icon": "⚠",
        "bg_color": "#fffbeb",
        "border_color": "#fde68a",
        "icon_color": "#d97706",
        "title_color": "#92400e",
        "text_color": "#b45309",
        "default_title": "Cảnh báo",
    },
    NotificationType.INFO: {
        "icon": "ℹ",
        "bg_color": "#eff6ff",
        "border_color": "#bfdbfe",
        "icon_color": "#2563eb",
        "title_color": "#1e40af",
        "text_color": "#1d4ed8",
        "default_title": "Thông báo",
    },
}


class ToastNotification(QFrame):
    """
    Thông báo nổi (Toast Notification) xuất hiện mượt mà ở góc trên bên phải,
    có hiệu ứng mờ dần (fade-in, fade-out) và tự động đóng sau khoảng thời gian.
    """

    _active_toasts = []

    def __init__(
        self,
        message: str,
        notif_type: NotificationType = NotificationType.INFO,
        title: str = None,
        duration: int = 3000,
        parent=None,
    ):
        super().__init__(parent)

        cfg = _TYPE_CONFIG.get(notif_type, _TYPE_CONFIG[NotificationType.INFO])
        title = title or cfg["default_title"]

        self.duration = duration
        self.setWindowFlags(
            Qt.WindowType.SubWindow
            | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedWidth(340)

        # Style
        self.setStyleSheet(f"""
            QFrame#toastFrame {{
                background-color: {cfg["bg_color"]};
                border: 1px solid {cfg["border_color"]};
                border-radius: 10px;
            }}

            QLabel#toastIcon {{
                color: {cfg["icon_color"]};
                font-size: 18px;
                font-weight: bold;
                background: transparent;
            }}

            QLabel#toastTitle {{
                color: {cfg["title_color"]};
                font-size: 13px;
                font-weight: 700;
                background: transparent;
            }}

            QLabel#toastMessage {{
                color: {cfg["text_color"]};
                font-size: 12px;
                background: transparent;
            }}

            QPushButton#toastClose {{
                border: none;
                background: transparent;
                color: #94a3b8;
                font-size: 13px;
                font-weight: bold;
                border-radius: 8px;
                padding: 2px 6px;
            }}

            QPushButton#toastClose:hover {{
                background-color: rgba(0, 0, 0, 0.06);
                color: #475569;
            }}
        """)

        self.setObjectName("toastFrame")

        # Layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(14, 12, 12, 12)
        main_layout.setSpacing(10)

        icon_label = QLabel(cfg["icon"])
        icon_label.setObjectName("toastIcon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)

        title_label = QLabel(title)
        title_label.setObjectName("toastTitle")

        message_label = QLabel(message)
        message_label.setObjectName("toastMessage")
        message_label.setWordWrap(True)

        text_layout.addWidget(title_label)
        text_layout.addWidget(message_label)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("toastClose")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close_animated)

        main_layout.addWidget(icon_label)
        main_layout.addLayout(text_layout, 1)
        main_layout.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignTop)

        # Opacity effect for animations
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)

        # Auto-close timer
        if self.duration > 0:
            self.timer = QTimer(self)
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.close_animated)

        # Position and show
        self._position_toast()
        ToastNotification._active_toasts.append(self)
        self.show()
        self._fade_in()

    def _position_toast(self):
        """Định vị toast ở góc trên bên phải của cửa sổ cha hoặc màn hình."""
        parent_widget = self.parent() or self.window()
        margin = 20
        spacing = 10

        if parent_widget and parent_widget.isVisible():
            parent_geo = parent_widget.geometry()
            x = parent_geo.width() - self.width() - margin
            y = margin
        else:
            x = margin
            y = margin

        # Tính toán offset nếu có nhiều toast đang hiển thị cùng lúc
        for existing in ToastNotification._active_toasts:
            if existing is not self and existing.isVisible():
                y += existing.height() + spacing

        self.move(x, y)

    def _fade_in(self):
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(250)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

        if self.duration > 0:
            self.anim.finished.connect(lambda: self.timer.start(self.duration))

    def close_animated(self):
        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()

        self.anim_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_out.setDuration(200)
        self.anim_out.setStartValue(self.opacity_effect.opacity())
        self.anim_out.setEndValue(0.0)
        self.anim_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self.anim_out.finished.connect(self._cleanup)
        self.anim_out.start()

    def _cleanup(self):
        if self in ToastNotification._active_toasts:
            ToastNotification._active_toasts.remove(self)
        self.close()
        self.deleteLater()


class NotificationBanner(QFrame):
    """
    Banner thông báo nhúng trực tiếp trong giao diện trang (inline alert).
    Có thể đặt ở đầu form, bảng dữ liệu để hiển thị thông tin, cảnh báo, lỗi.
    """

    def __init__(
        self,
        message: str = "",
        notif_type: NotificationType = NotificationType.INFO,
        dismissible: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self.dismissible = dismissible
        self.init_ui()
        if message:
            self.set_message(message, notif_type)
        else:
            self.hide()

    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(14, 10, 14, 10)
        self.layout.setSpacing(10)

        self.icon_label = QLabel()
        self.icon_label.setStyleSheet("font-size: 16px; font-weight: bold; background: transparent;")

        self.message_label = QLabel()
        self.message_label.setStyleSheet("font-size: 13px; background: transparent;")
        self.message_label.setWordWrap(True)

        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.message_label, 1)

        if self.dismissible:
            self.close_btn = QPushButton("✕")
            self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.close_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                    color: #94a3b8;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 2px 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.05);
                    color: #475569;
                }
            """)
            self.close_btn.clicked.connect(self.hide)
            self.layout.addWidget(self.close_btn)

    def set_message(self, message: str, notif_type: NotificationType = NotificationType.INFO):
        """Cập nhật nội dung và loại thông báo."""
        cfg = _TYPE_CONFIG.get(notif_type, _TYPE_CONFIG[NotificationType.INFO])

        self.setStyleSheet(f"""
            NotificationBanner {{
                background-color: {cfg["bg_color"]};
                border: 1px solid {cfg["border_color"]};
                border-radius: 8px;
            }}
        """)

        self.icon_label.setText(cfg["icon"])
        self.icon_label.setStyleSheet(f"color: {cfg['icon_color']}; font-size: 16px; font-weight: bold; background: transparent;")

        self.message_label.setText(message)
        self.message_label.setStyleSheet(f"color: {cfg['text_color']}; font-size: 13px; background: transparent;")

        self.show()


class Notification:
    """
    Tiện ích gọi nhanh thông báo dạng Toast từ bất kỳ vị trí nào trong ứng dụng.
    """

    @staticmethod
    def show(
        parent,
        message: str,
        notif_type: NotificationType = NotificationType.INFO,
        title: str = None,
        duration: int = 3000,
    ) -> ToastNotification:
        return ToastNotification(
            message=message,
            notif_type=notif_type,
            title=title,
            duration=duration,
            parent=parent,
        )

    @staticmethod
    def success(parent, message: str, title: str = "Thành công", duration: int = 3000) -> ToastNotification:
        return Notification.show(parent, message, NotificationType.SUCCESS, title, duration)

    @staticmethod
    def error(parent, message: str, title: str = "Lỗi", duration: int = 4000) -> ToastNotification:
        return Notification.show(parent, message, NotificationType.ERROR, title, duration)

    @staticmethod
    def warning(parent, message: str, title: str = "Cảnh báo", duration: int = 3500) -> ToastNotification:
        return Notification.show(parent, message, NotificationType.WARNING, title, duration)

    @staticmethod
    def info(parent, message: str, title: str = "Thông báo", duration: int = 3000) -> ToastNotification:
        return Notification.show(parent, message, NotificationType.INFO, title, duration)
