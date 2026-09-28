"""Bộ kiểm tra ký tự dùng chung cho các ô nhập liệu trên giao diện."""

import unicodedata

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QValidator
from PyQt6.QtWidgets import QComboBox, QLabel, QVBoxLayout, QWidget


ALLOWED_SPECIAL_CHARACTERS = "+-./()&#"


def text_input_error(value, *, allow_digits=True):
    """Trả về mô tả lỗi của chuỗi, hoặc ``None`` nếu chuỗi hợp lệ."""
    if value.startswith(" "):
        return "không được bắt đầu bằng khoảng trắng"
    if "  " in value:
        return "không được chứa hai khoảng trắng liên tiếp"

    for character in value:
        category = unicodedata.category(character)
        is_letter = character.isalpha() or category.startswith("M")
        if is_letter or character == " " or character in ALLOWED_SPECIAL_CHARACTERS:
            continue
        if allow_digits and character.isdigit():
            continue
        if character.isdigit():
            return "không được chứa chữ số"
        return (
            "chỉ được chứa chữ cái"
            + (", chữ số" if allow_digits else "")
            + ", khoảng trắng và các ký tự + - . / ( ) & #"
        )
    return None


def is_duplicate_error(message):
    """Nhận diện thông báo trùng dữ liệu do backend trả về."""
    normalized = unicodedata.normalize("NFD", str(message).casefold())
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
    normalized = normalized.replace("đ", "d")
    return "da ton tai" in normalized or "bi trung" in normalized


class TextInputValidator(QValidator):
    """Chỉ chặn khoảng trắng đầu chuỗi và hai khoảng trắng liên tiếp."""

    def __init__(self, parent=None):
        super().__init__(parent)

    def validate(self, value, position):
        if not value:
            return QValidator.State.Intermediate, value, position
        if value.startswith(" ") or "  " in value:
            return QValidator.State.Invalid, value, position
        return QValidator.State.Acceptable, value, position


def apply_text_validator(line_edit):
    """Gắn bộ chặn khoảng trắng vào QLineEdit."""
    validator = TextInputValidator(parent=line_edit)
    line_edit.setValidator(validator)
    return validator


def add_inline_validation(form, title, field):
    """Thêm vùng hiển thị lỗi ngay dưới field."""
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)
    layout.addWidget(field)

    error_label = QLabel()
    error_label.setObjectName("fieldError")
    error_label.setWordWrap(True)
    error_label.hide()
    layout.addWidget(error_label)
    form.addRow(title, container)

    if isinstance(field, QComboBox):
        editor = field.lineEdit()
        if editor is not None:
            editor.textEdited.connect(
                lambda: clear_field_error(field, error_label)
            )
        else:
            field.currentIndexChanged.connect(
                lambda: clear_field_error(field, error_label)
            )
    elif hasattr(field, "textEdited"):
        field.textEdited.connect(lambda: clear_field_error(field, error_label))
    elif hasattr(field, "textChanged"):
        field.textChanged.connect(lambda: clear_field_error(field, error_label))
    return error_label


def clear_field_error(field, error_label):
    """Bỏ viền đỏ và lỗi khi người dùng bắt đầu nhập lại."""
    field.setProperty("invalid", False)
    field.style().unpolish(field)
    field.style().polish(field)
    error_label.clear()
    error_label.hide()


def show_field_error(field, error_label, message):
    """Xóa field sai và hiện lỗi trong 1,5 giây."""
    if isinstance(field, QComboBox):
        field.setCurrentIndex(-1)
        if field.isEditable():
            field.setEditText("")
    else:
        field.clear()
    field.setProperty("invalid", True)
    field.style().unpolish(field)
    field.style().polish(field)
    error_label.setText(message)
    error_label.show()

    error_version = (field.property("errorVersion") or 0) + 1
    field.setProperty("errorVersion", error_version)

    def hide_current_error():
        if field.property("errorVersion") == error_version:
            clear_field_error(field, error_label)

    timer = QTimer(field)
    timer.setSingleShot(True)
    timer.timeout.connect(hide_current_error)
    timer.timeout.connect(timer.deleteLater)
    timer.start(1500)


def show_temporary_message(label, message, *, status="success", duration=750):
    """Hiện thông báo trong biểu mẫu rồi tự ẩn sau ``duration`` mili giây."""
    message_version = (label.property("messageVersion") or 0) + 1
    label.setProperty("messageVersion", message_version)
    label.setProperty("status", status)
    label.style().unpolish(label)
    label.style().polish(label)
    label.setWordWrap(True)
    label.setText(message)
    label.show()

    def hide_current_message():
        if label.property("messageVersion") == message_version:
            label.clear()
            label.hide()

    timer = QTimer(label)
    timer.setSingleShot(True)
    timer.timeout.connect(hide_current_message)
    timer.timeout.connect(timer.deleteLater)
    timer.start(duration)
