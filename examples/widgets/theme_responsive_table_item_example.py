import sys

import qtawesome
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QTableWidget

from extra_qwidgets.widgets.theme_responsive_table_item import QThemeResponsiveTableItem
from source.extra_qwidgets.utils import colorize_icon_by_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Theme Responsive Table Item Test")
        self.setWindowIcon(colorize_icon_by_theme(qtawesome.icon("fa6b.python")))
        self.setFixedSize(800, 600)

        widget = QWidget()

        layout = QVBoxLayout()

        table_widget = QTableWidget()
        table_widget.setColumnCount(1)
        for i in range(0, 10):
            item = QThemeResponsiveTableItem()
            item.setText(f"Item {i}")
            item.setIcon(qtawesome.icon("fa6s.face-smile"))
            table_widget.insertRow(table_widget.rowCount())
            table_widget.setItem(table_widget.rowCount() - 1, 0, item)

        layout.addWidget(table_widget)

        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())