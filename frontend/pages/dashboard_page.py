"""Trang tổng quan hệ thống quản lý tín chỉ PTIT."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from PyQt6.QtCore import (
    QByteArray,
    QSize, Qt, pyqtSignal,
)
from frontend.components.branding import CampusBackground, PtitBrand, SidebarNavButton
from frontend.components.topbar import TopBar

from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QHeaderView, QLabel, QMainWindow,
    QPushButton, QScrollArea, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget,
)


RESOURCES = Path(__file__).resolve().parents[1] / "resources"
ICONS = RESOURCES / "icons"
IMAGES = RESOURCES / "images"


def svg_pixmap(filename, tint="#ffffff", size=28):
    path = ICONS / filename
    if not path.exists():
        return QPixmap()
    source = path.read_text(encoding="utf-8").replace("currentColor", tint)
    pixmap = QPixmap(size * 2, size * 2)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    QSvgRenderer(QByteArray(source.encode())).render(painter)
    painter.end()
    pixmap.setDevicePixelRatio(2)
    return pixmap


def svg_label(filename, tint, size):
    label = QLabel()
    label.setFixedSize(size, size)
    label.setPixmap(svg_pixmap(filename, tint, size))
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setStyleSheet("background: transparent; border: none;")
    return label


def status_badge(text, tone):
    colors = {
        "green": ("#dcfce7", "#15803d", "#86efac"),
        "yellow": ("#fef3c7", "#b45309", "#fcd34d"),
        "red": ("#fee2e2", "#dc2626", "#fca5a5"),
        "blue": ("#dbeafe", "#1d4ed8", "#93c5fd"),
    }
    background, foreground, border = colors[tone]
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(4, 2, 4, 2)
    label = QLabel(text)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setMinimumWidth(90)
    label.setFixedHeight(26)
    label.setStyleSheet(f"""
        QLabel {{
            color: {foreground}; background: {background};
            border: 1px solid {border}; border-radius: 12px;
            padding: 1px 8px; font-size: 12px; font-weight: 600;
        }}
    """)
    layout.addStretch()
    layout.addWidget(label)
    layout.addStretch()
    return container


class EmptyStateTable(QTableWidget):
    """Bảng vẫn hiện tiêu đề cột và báo trạng thái khi chưa có dữ liệu."""

    def __init__(self, headers, parent=None):
        super().__init__(0, len(headers), parent)
        self.setHorizontalHeaderLabels(headers)
        self.verticalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.empty_label = QLabel("Chưa có dữ liệu", self.viewport())
        self.empty_label.setObjectName("emptyTableLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._sync_empty_state()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.empty_label.setGeometry(self.viewport().rect())

    def set_rows(self, rows=None):
        self.setRowCount(0)
        for row_values in rows or []:
            row = self.rowCount()
            self.insertRow(row)
            for column, value in enumerate(row_values[:self.columnCount()]):
                if column == 5:
                    status = str(value)
                    tone = "red" if "đã hủy" in status.casefold() else "yellow"
                    self.setCellWidget(row, column, status_badge(status, tone))
                    continue
                item = QTableWidgetItem(str(value))
                if column in (0, 1, 2, 3, 4):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                    )
                self.setItem(row, column, item)
            self.setRowHeight(row, 38)
        self._sync_empty_state()

    def _sync_empty_state(self):
        self.empty_label.setVisible(self.rowCount() == 0)
        self.empty_label.raise_()


class StatCard(QFrame):
    def __init__(self, icon, caption, accent, pale, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setMinimumHeight(100)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        circle = QFrame()
        circle.setFixedSize(64, 64)
        circle.setStyleSheet(
            f"background: {pale}; border: none; border-radius: 32px;"
        )
        circle_layout = QVBoxLayout(circle)
        circle_layout.setContentsMargins(14, 14, 14, 14)
        circle_layout.addWidget(svg_label(icon, accent, 36))

        labels = QVBoxLayout()
        labels.setSpacing(0)
        self.value_label = QLabel("0")
        self.value_label.setObjectName("statValue")
        self.value_label.setStyleSheet(f"color: {accent};")
        caption_label = QLabel(caption)
        caption_label.setObjectName("statCaption")
        labels.addWidget(self.value_label)
        labels.addWidget(caption_label)
        layout.addWidget(circle)
        layout.addLayout(labels, 1)

    def set_value(self, value=0):
        try:
            number = int(value or 0)
        except (TypeError, ValueError):
            number = 0
        self.value_label.setText(f"{number:,}".replace(",", "."))


class DashboardPage(QWidget):
    """Dashboard hoàn chỉnh với dữ liệu mặc định bằng 0/rỗng."""

    navigation_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dashboardPage")
        self.setMinimumSize(1050, 680)
        self._build_ui()
        self._apply_style()
        self.set_statistics()
        self.set_attention_rows()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_sidebar())

        right = QWidget()
        right.setObjectName("dashboardRight")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self._build_topbar())

        scroll = QScrollArea()
        scroll.setObjectName("dashboardScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(self._build_content())
        right_layout.addWidget(scroll, 1)
        root.addWidget(right, 1)

    def _build_sidebar(self):
        sidebar = CampusBackground()
        sidebar.setObjectName("dashboardSidebar")
        sidebar.setFixedWidth(210)
        self.sidebar = sidebar
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 8, 10, 16)
        layout.setSpacing(7)

        brand = PtitBrand()
        self.brand_subtitle = brand.subtitle
        layout.addWidget(brand)

        menu_items = [
            ("dashboard", "home.svg", "Trang chủ"),
            ("student", "class.svg", "Lớp & Sinh viên"),
            ("subject", "subject.svg", "Môn học"),
            ("credit_class", "credit_class.svg", "Lớp tín chỉ"),
            ("registration", "registration.svg", "Đăng ký học"),
            ("score", "score.svg", "Nhập điểm"),
        ]
        self.nav_buttons = {}
        for key, icon_name, caption in menu_items:
            button = SidebarNavButton(caption)
            button.setObjectName("sidebarNavButton")
            button.setCheckable(True)
            button.setIcon(QIcon(svg_pixmap(icon_name, "#ffffff", 25)))
            button.setIconSize(QSize(25, 25))
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda _checked=False, page=key: self.select_page(page)
            )
            self.nav_buttons[key] = button
            layout.addWidget(button)
        layout.addStretch()
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: #6690b1; border: none;")
        layout.addWidget(separator)
        self.select_page("dashboard", emit_signal=False)
        return sidebar

    def _build_topbar(self):
        return TopBar()

    def _build_content(self):
        content = QWidget()
        content.setObjectName("dashboardContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(15)

        self.term_label = QLabel("Học kỳ 1 · Niên khóa 2026–2027")
        self.term_label.setObjectName("dashboardTerm")
        layout.addWidget(self.term_label)

        stats = QHBoxLayout()
        stats.setSpacing(13)
        definitions = [
            ("students", "student.svg", "Sinh viên", "#087cf0", "#d9f2ff"),
            ("classes", "building.svg", "Lớp niên chế", "#047857", "#d8f8ec"),
            ("subjects", "subject.svg", "Môn học", "#d20a2e", "#ffe0e6"),
            ("credit_classes", "class.svg", "Lớp tín chỉ", "#ed7b00", "#ffecd6"),
        ]
        self.stat_cards = {}
        for key, icon_name, caption, accent, pale in definitions:
            card = StatCard(icon_name, caption, accent, pale)
            self.stat_cards[key] = card
            stats.addWidget(card, 1)
        layout.addLayout(stats)

        lower = QHBoxLayout()
        lower.setSpacing(10)
        lower.addWidget(self._build_attention_card(), 7)
        lower.addWidget(self._build_quick_actions(), 3)
        layout.addLayout(lower, 1)
        return content

    def _build_attention_card(self):
        card = QFrame()
        card.setObjectName("dashboardCard")
        card.setMinimumHeight(430)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 14, 15, 15)
        layout.setSpacing(9)
        heading = QHBoxLayout()
        heading.setSpacing(12)
        heading.addWidget(svg_label("warning.svg", "#f59e0b", 32))
        title = QLabel("Lớp tín chỉ cần chú ý")
        title.setObjectName("sectionTitle")
        heading.addWidget(title)
        heading.addStretch()
        view_all = QPushButton("Xem tất cả")
        view_all.setObjectName("viewAllButton")
        view_all.setIcon(QIcon(svg_pixmap("chevron_right.svg", "#087cf0", 16)))
        view_all.setIconSize(QSize(16, 16))
        view_all.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        view_all.setCursor(Qt.CursorShape.PointingHandCursor)
        view_all.clicked.connect(lambda: self.navigation_requested.emit("credit_class"))
        heading.addWidget(view_all)
        layout.addLayout(heading)
        self.attention_table = EmptyStateTable(
            [
                "Mã lớp tín chỉ", "Mã môn học", "Nhóm",
                "Đã đăng ký", "Tối thiểu", "Trạng thái",
            ]
        )
        layout.addWidget(self.attention_table, 1)
        return card

    def _build_quick_actions(self):
        card = QFrame()
        card.setObjectName("dashboardCard")
        card.setMinimumWidth(280)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 14, 15, 15)
        layout.setSpacing(15)
        heading = QHBoxLayout()
        heading.addWidget(svg_label("fast.svg", "#d5cc27", 31))
        title = QLabel("Thao tác nhanh")
        title.setObjectName("sectionTitle")
        heading.addWidget(title)
        heading.addStretch()
        layout.addLayout(heading)

        actions = [
            ("open_credit_class", "plus.svg", "Mở lớp tín chỉ", "green", "#059669"),
            ("registration", "file_text.svg", "Đăng ký học", "blue", "#087cf0"),
            ("score", "score.svg", "Nhập điểm", "orange", "#e87900"),
        ]
        for key, icon_name, caption, theme, accent in actions:
            button = QPushButton(caption)
            button.setObjectName("quickActionButton")
            button.setProperty("theme", theme)
            button.setIcon(QIcon(svg_pixmap(icon_name, accent, 34)))
            button.setIconSize(QSize(34, 34))
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda _checked=False, page=key: self.navigation_requested.emit(page)
            )
            layout.addWidget(button)
        layout.addStretch()
        return card

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#dashboardPage, QWidget#dashboardRight, QWidget#dashboardContent {
                background-color: #f3f9fd; color: #0f172a; font-family: "Segoe UI";
            }
            QScrollArea#dashboardScroll { background: transparent; border: none; }
            QScrollArea#dashboardScroll > QWidget > QWidget { background: #f3f9fd; }
            QFrame#dashboardSidebar { background: transparent; border: none; }
            QLabel#brandTitle { color: #ff2d36; font-size: 29px; font-weight: 700; font-style: italic; }
            QLabel#brandSubtitle { color: #7dd3fc; font-size: 12px; font-weight: 600; }
            QFrame#dashboardTopbar { background: white; border: none; border-bottom: 1px solid #e2e8f0; }
            QLabel#topbarTitle { color: #0f2b4c; font-size: 17px; font-weight: 700; }
            QLabel#dashboardTerm { color: #4f6f9c; font-size: 18px; }
            QFrame#statCard, QFrame#dashboardCard {
                background: white; border: 1px solid #d8e2ef; border-radius: 9px; padding: 0;
            }
            QLabel#statValue { font-size: 34px; font-weight: 700; }
            QLabel#statCaption { color: #365b8d; font-size: 17px; }
            QLabel#sectionTitle { color: #0f2b4c; font-size: 18px; font-weight: 700; }
            QPushButton#viewAllButton {
                background: transparent; border: none; color: #087cf0; font-size: 14px; padding: 6px 2px;
            }
            QPushButton#viewAllButton:hover { color: #075bbf; }
            QTableWidget {
                background: white; alternate-background-color: #f8fafc; border: 1px solid #d8e2ef;
                border-radius: 7px; gridline-color: #e2e8f0; color: #0f2b4c; font-size: 13px;
            }
            QTableWidget::item { padding: 4px 7px; }
            QHeaderView::section {
                background: #eef4f9; color: #0f2b4c; font-size: 13px; font-weight: 700;
                padding: 10px 8px; border: none; border-right: 1px solid #d8e2ef;
                border-bottom: 1px solid #d8e2ef;
            }
            QLabel#emptyTableLabel { color: #94a3b8; font-size: 15px; background: white; }
            QPushButton#quickActionButton {
                min-height: 42px; border-radius: 7px; text-align: left;
                padding: 7px 14px; font-size: 15px; font-weight: 700;
            }
            QPushButton#quickActionButton[theme="green"] { color: #047857; background: #e8fbf5; border: 1px solid #a8ead5; }
            QPushButton#quickActionButton[theme="blue"] { color: #087cf0; background: #edf6ff; border: 1px solid #acd2ff; }
            QPushButton#quickActionButton[theme="orange"] { color: #c65f00; background: #fff5e8; border: 1px solid #ffd091; }
            QPushButton#quickActionButton:hover { border-width: 2px; }
        """)

    def select_page(self, page_name, emit_signal=True):
        for key, button in self.nav_buttons.items():
            button.setChecked(key == page_name)
        if emit_signal:
            self.navigation_requested.emit(page_name)

    def set_term(self, semester=1, academic_year="2026–2027"):
        self.term_label.setText(f"Học kỳ {semester} · Niên khóa {academic_year}")

    def set_statistics(self, students=0, classes=0, subjects=0, credit_classes=0):
        for key, value in {
            "students": students,
            "classes": classes,
            "subjects": subjects,
            "credit_classes": credit_classes,
        }.items():
            self.stat_cards[key].set_value(value)

    def set_attention_rows(self, rows=None):
        """Rows: mã LTC, môn học, nhóm, đã đăng ký, tối thiểu, trạng thái."""
        self.attention_table.set_rows(rows or [])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qss = RESOURCES / "styles" / "ptit.qss"
    if qss.exists():
        stylesheet = qss.read_text(encoding="utf-8")
        stylesheet = stylesheet.replace(
            "__CHEVRON_DOWN_ICON__", (ICONS / "chevron_down.svg").as_posix()
        ).replace(
            "__CHEVRON_UP_ICON__", (ICONS / "chevron_up.svg").as_posix()
        )
        app.setStyleSheet(stylesheet)
    window = QMainWindow()
    window.setWindowTitle("Dashboard - Hệ thống quản lý tín chỉ")
    window.resize(1536, 900)
    window.setMinimumSize(1050, 680)
    window.setCentralWidget(DashboardPage())
    window.show()
    raise SystemExit(app.exec())
