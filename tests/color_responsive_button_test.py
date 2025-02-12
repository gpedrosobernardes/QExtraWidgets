import sys

from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout

from source.extra_qwidgets.widgets import QColorResponsiveButton
from source.extra_qwidgets.utils import colorize_icon_by_theme, get_icon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Color Responsive Button Test")
        self.setWindowIcon(colorize_icon_by_theme(get_icon("python-brands-solid.svg")))

        widget = QWidget()

        layout = QVBoxLayout()

        button = QColorResponsiveButton()
        button.setIcon(get_icon("face-smile-solid.svg"))

        layout.addWidget(button)

        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())