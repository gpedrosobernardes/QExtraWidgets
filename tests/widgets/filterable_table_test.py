import sys

import qtawesome
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout

from extra_qwidgets.widgets.filterable_table.filterable_table import QFilterableTable
from source.extra_qwidgets.proxys import colorize_icon_by_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Filterable Table Test")
        self.setWindowIcon(colorize_icon_by_theme(qtawesome.icon("fa6b.python")))
        self.setFixedSize(800, 600)

        widget = QWidget()

        layout = QVBoxLayout()

        table = QFilterableTable()
        model = table.model()
        model.setColumnCount(1)
        for i in range(0, 1000):
            model.insertRow(i)
            model.setItem(i, 0, QStandardItem(f"Item {i}"))

        layout.addWidget(table)

        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())