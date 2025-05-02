import sys

import qtawesome
from PySide6.QtWidgets import QMainWindow, QApplication
from qfluentwidgets import Theme, setTheme

from extra_qwidgets.fluent_widgets.single_selection_list import SingleSelectionList
from source.extra_qwidgets.proxys import colorize_icon_by_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Single Selection List Test")
        self.setWindowIcon(colorize_icon_by_theme(qtawesome.icon("fa6b.python")))

        items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6", "Item 7", "Item 8", "Item 9", "Item 10"]

        fluent_widget = SingleSelectionList()
        fluent_widget.addToSelectItems(items)

        self.setCentralWidget(fluent_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    setTheme(Theme.AUTO)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())