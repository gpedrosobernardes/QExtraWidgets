import sys

import qtawesome
from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QCheckBox

from extra_qwidgets.widgets.checkboxes import QCheckBoxes
from source.extra_qwidgets.proxys import colorize_icon_by_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Checkboxes Test")
        self.setFixedWidth(275)
        self.setWindowIcon(colorize_icon_by_theme(qtawesome.icon("fa6b.python")))

        widget = QCheckBoxes(QLabel("Select a color:"))
        widget.addCheckboxes(QCheckBox("Red"), QCheckBox("Green"), QCheckBox("Blue"))

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())