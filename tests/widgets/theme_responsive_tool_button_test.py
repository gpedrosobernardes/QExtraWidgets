import sys

import qtawesome
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout

from extra_qwidgets.widgets.theme_responsive_tool_button import QThemeResponsiveToolButton
from source.extra_qwidgets.utils import colorize_icon_by_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Theme Responsive Tool Button Test")
        self.setWindowIcon(colorize_icon_by_theme(qtawesome.icon("fa6b.python")))
        self.setFixedSize(350, 100)

        widget = QWidget()

        layout = QVBoxLayout()

        button = QThemeResponsiveToolButton()
        button.setIcon(qtawesome.icon("fa6s.face-smile"))

        layout.addWidget(button)

        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())