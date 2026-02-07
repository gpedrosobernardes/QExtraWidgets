from qextrawidgets.widgets.inputs import QPasswordLineEdit
import sys

from PySide6.QtWidgets import QApplication, QHBoxLayout, QWidget

from qextrawidgets.gui.icons import QThemeResponsiveIcon


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QPasswordLineEdit Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        self._init_widgets()
        self.setup_layout()
        self.setup_connections()

    def _init_widgets(self) -> None:
        self.password_edit = QPasswordLineEdit()

    def setup_layout(self) -> None:
        layout = QHBoxLayout()
        layout.addWidget(self.password_edit)
        self.setLayout(layout)

    def setup_connections(self) -> None:
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
