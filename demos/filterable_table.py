from qextrawidgets.widgets.views.filterable_table_view import QFilterableTableView
import sys
import random
from datetime import datetime, timedelta

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QHBoxLayout,
    QHeaderView,
)

from qextrawidgets.gui.icons import QThemeResponsiveIcon


class DemoTableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QFilterableTable Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))
        self.resize(800, 600)

        self._init_widgets()
        self.setup_layout()
        self.setup_connections()

        # 3. Populate Data
        self.populate_data()

    def _init_widgets(self) -> None:
        # 1. Instructions Header
        self.lbl_instr = QLabel(
            "<h3>Instructions:</h3>"
            "<ul>"
            "<li>Click on the <b>filter icon</b> (header) to open the Popup.</li>"
            "<li>Test <b>Select All</b> and <b>Search</b>.</li>"
            "<li>Check if the popup list is sorted alphabetically.</li>"
            "</ul>"
        )
        self.lbl_instr.setWordWrap(True)

        # 2. The Filterable Table
        self.table = QFilterableTableView()
        self.table.setAlternatingRowColors(True)

        # Style for better visualization (Columns fill the space)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

    def setup_layout(self) -> None:
        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 1. Header / Instructions
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.lbl_instr)

        layout.addLayout(header_layout)

        # 2. The Filterable Table
        layout.addWidget(self.table)

    def setup_connections(self) -> None:
        pass

    def populate_data(self):
        """Creates a model with dummy data for testing."""
        model = QStandardItemModel()

        # Columns
        headers = ["ID", "Name", "Department", "Status", "Date", "Priority"]
        model.setHorizontalHeaderLabels(headers)

        # Dummy Data
        departments = ["IT", "HR", "Finance", "Sales", "Logistics"]
        names = [
            "James",
            "John",
            "William",
            "Henry",
            "George",
            "Edward",
            "Thomas",
            "Charles",
            "Arthur",
            "Robert",
        ]
        statuses = ["Active", "Inactive", "Pending", "Vacation"]
        priorities = ["High", "Medium", "Low"]

        # Generate 100 rows
        for i in range(1, 101):
            row_items = []

            # ID
            it_id = QStandardItem()
            it_id.setData(i, Qt.ItemDataRole.DisplayRole)
            row_items.append(it_id)

            # Name
            last_names = [
                "Smith",
                "Johnson",
                "Brown",
                "Taylor",
                "Anderson",
                "Thompson",
                "Harris",
                "Walker",
                "White",
                "Clark",
            ]
            name = f"{random.choice(names)} {random.choice(last_names)}"
            row_items.append(QStandardItem(name))

            # Department
            row_items.append(QStandardItem(random.choice(departments)))

            # Status
            status = random.choice(statuses)
            it_status = QStandardItem(status)

            # Example of simple conditional formatting
            if status == "Active":
                it_status.setForeground(QColor("green"))
            elif status == "Inactive":
                it_status.setForeground(QColor("red"))

            row_items.append(it_status)

            # Date
            date = datetime.now() - timedelta(days=random.randint(0, 365))
            row_items.append(QStandardItem(date.strftime("%Y-%m-%d")))

            # Priority
            row_items.append(QStandardItem(random.choice(priorities)))

            model.appendRow(row_items)

        # Injects the model into the table
        self.table.setModel(model)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemoTableWindow()
    window.show()
    sys.exit(app.exec())
