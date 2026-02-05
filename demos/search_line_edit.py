import sys

from PySide6.QtWidgets import QApplication, QHBoxLayout, QWidget

from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets import QSearchLineEdit


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QSearchLineEdit Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        widget = QSearchLineEdit()

        layout = QHBoxLayout()

        layout.addWidget(widget)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())