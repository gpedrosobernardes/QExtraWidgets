import sys

import qtawesome
from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QWidget, QVBoxLayout

from extra_qwidgets.utils import colorize_icon_by_theme
from source.extra_qwidgets.widgets.collapse_group import QCollapseGroup


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Collapse Group Test")
        self.setWindowIcon(colorize_icon_by_theme(qtawesome.icon("fa6b.python")))

        widget = QWidget()

        layout = QVBoxLayout()

        collapse_group = QCollapseGroup()
        collapse_group.addCollapse("Test 1", QLabel("Hello World!"))
        collapse_group.addCollapse("Test 2", QLabel("Hello World 2!"))
        layout.addWidget(collapse_group)

        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())