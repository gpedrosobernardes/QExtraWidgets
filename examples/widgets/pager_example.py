import sys

import qtawesome
from PySide6.QtWidgets import QApplication, QMainWindow

from extra_qwidgets.utils import colorize_icon_by_theme
from extra_qwidgets.widgets.pager import QPager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pager Test")
        self.setWindowIcon(colorize_icon_by_theme(qtawesome.icon("fa6b.python")))

        pager = QPager()

        self.setCentralWidget(pager)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())