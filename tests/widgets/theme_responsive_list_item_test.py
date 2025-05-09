import sys

import qtawesome
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QListWidget

from extra_qwidgets.widgets.theme_responsive_list_item import QThemeResponsiveListItem
from source.extra_qwidgets.utils import colorize_icon_by_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Theme Responsive List Item Test")
        self.setWindowIcon(colorize_icon_by_theme(qtawesome.icon("fa6b.python")))
        self.setFixedSize(800, 600)

        widget = QWidget()

        layout = QVBoxLayout()

        list_widget = QListWidget()
        for i in range(0, 10):
            item = QThemeResponsiveListItem()
            item.setIcon(qtawesome.icon("fa6s.face-smile"))
            list_widget.addItem(item)

        layout.addWidget(list_widget)

        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())