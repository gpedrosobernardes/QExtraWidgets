import sys

from PySide6.QtWidgets import QMainWindow, QApplication

from extra_qwidgets.icons import QThemeResponsiveIcon
from extra_qwidgets.widgets.dual_list import QDualList


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Single Selection List Example")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6", "Item 7", "Item 8", "Item 9", "Item 10"]

        widget = QDualList()
        widget.setAvailableItems(items)

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())