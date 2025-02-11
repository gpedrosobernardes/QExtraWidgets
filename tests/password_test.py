import sys

from PySide6.QtWidgets import QMainWindow, QApplication

from widgets.password import QPassword


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Password Test")

        widget = QPassword()

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())