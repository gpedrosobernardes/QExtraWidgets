import sys

from PySide6.QtWidgets import QApplication, QHBoxLayout, QWidget

from extra_qwidgets.icons import QThemeResponsiveIcon
from extra_qwidgets.widgets.password import QPassword


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Password Example")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        widget = QPassword()

        layout = QHBoxLayout()

        layout.addWidget(widget)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())