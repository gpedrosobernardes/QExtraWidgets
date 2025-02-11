import sys

from PySide6.QtWidgets import QMainWindow, QApplication

from widgets.single_selection_list import QSingleSelectionList
from widgets.utils import colorize_icon, get_icon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Single Selection List Test")
        self.setWindowIcon(colorize_icon(get_icon("python-brands-solid.svg"), "#FFFFFF"))

        widget = QSingleSelectionList()
        widget.add_to_select_items(["Item 1", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6", "Item 7", "Item 8", "Item 9", "Item 10"])

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())