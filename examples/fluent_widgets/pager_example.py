import sys

import qtawesome
from PySide6.QtWidgets import QApplication, QMainWindow
from qfluentwidgets import setTheme, Theme

from extra_qwidgets.fluent_widgets.pager import Pager
from extra_qwidgets.utils import colorize_icon_by_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pager Test")
        self.setWindowIcon(colorize_icon_by_theme(qtawesome.icon("fa6b.python")))

        pager = Pager()
        pager.setVisibleButtonCount(3)
        pager.setPageCount(100)
        pager.setVisibleButtonCount(9)
        pager.setShortcutButtonsVisible(False)
        pager.currentPageChanged.connect(lambda page: print(f"Current page: {page}"))

        self.setCentralWidget(pager)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    setTheme(Theme.AUTO)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())