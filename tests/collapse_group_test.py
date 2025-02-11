import sys

from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QCheckBox, QWidget, QVBoxLayout

from widgets.collapse_group import QCollapseGroup
from widgets.utils import colorize_icon, get_icon, colorize_icon_by_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Collapse Group Test")
        self.setWindowIcon(colorize_icon_by_theme(get_icon("python-brands-solid.svg")))

        widget = QWidget()

        layout = QVBoxLayout()

        collapse_group = QCollapseGroup("Test", QLabel("Hello World!"))
        layout.addWidget(collapse_group)
        collapse_group_2 = QCollapseGroup("Test 2", QLabel("Hello World 2!"))
        layout.addWidget(collapse_group_2)

        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())