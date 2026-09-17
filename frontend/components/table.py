from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)


class DataTable(QTableWidget):

    def __init__(self, headers=None, parent=None):
        super().__init__(parent)

        if headers is None:
            headers = []

        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

        self.setup_table()

    def setup_table(self):
        self.setAlternatingRowColors(True)

        self.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.verticalHeader().setVisible(False)

        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.setObjectName("dataTable")
        self.setStyleSheet("""
            QTableWidget#dataTable {
                background-color: #ffffff;
                alternate-background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
                font-size: 13px;
                color: #1e293b;
                selection-background-color: #dcecff;
                selection-color: #0f2b4c;
            }

            QTableWidget#dataTable::item {
                padding: 8px 12px;
                border: none;
            }

            QTableWidget#dataTable::item:selected {
                background-color: #dcecff;
                color: #0f2b4c;
                font-weight: 500;
            }

            QTableWidget#dataTable::item:hover {
                background-color: #f1f5f9;
            }

            QHeaderView::section {
                background-color: #f1f5f9;
                color: #0f2b4c;
                font-size: 12.5px;
                font-weight: 600;
                padding: 10px 12px;
                border: none;
                border-bottom: 1.5px solid #cbd5e1;
                border-right: 1px solid #e2e8f0;
            }

            QHeaderView::section:last {
                border-right: none;
            }
        """)

    def set_data(self, rows):
        self.setRowCount(len(rows))

        for row_index, row_data in enumerate(rows):

            for column_index, value in enumerate(row_data):

                item = QTableWidgetItem(str(value))

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter
                    | Qt.AlignmentFlag.AlignLeft
                )

                self.setItem(
                    row_index,
                    column_index,
                    item
                )

    def clear_data(self):
        self.setRowCount(0)

    def get_selected_row(self):
        rows = self.selectionModel().selectedRows()

        if not rows:
            return -1

        return rows[0].row()

    def get_selected_row_data(self):
        row = self.get_selected_row()

        if row == -1:
            return None

        result = []

        for column in range(self.columnCount()):

            item = self.item(row, column)

            result.append(
                item.text() if item else ""
            )

        return result