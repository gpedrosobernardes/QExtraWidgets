import sys

from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QCheckBox

from widgets.checkbox_group import QCheckBoxGroup
from widgets.utils import get_icon, colorize_icon_by_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Checkbox Group Test")
        self.setWindowIcon(colorize_icon_by_theme(get_icon("python-brands-solid.svg")))

        widget = QCheckBoxGroup(QLabel("Select a color:"))
        widget.add_checkbox("red", QCheckBox("Red"))
        widget.add_checkbox("green", QCheckBox("Green"))
        widget.add_checkbox("blue", QCheckBox("Blue"))

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())