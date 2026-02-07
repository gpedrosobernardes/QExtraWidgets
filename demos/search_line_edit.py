from qextrawidgets.widgets.inputs.search_line_edit import QSearchLineEdit
import sys

from PySide6.QtWidgets import QApplication, QHBoxLayout, QWidget

from qextrawidgets.gui.icons import QThemeResponsiveIcon


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QSearchLineEdit Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        self._init_widgets()
        self.setup_layout()
        self.setup_connections()

    def _init_widgets(self) -> None:
        self.search_edit = QSearchLineEdit()

    def setup_layout(self) -> None:
        layout = QHBoxLayout()
        layout.addWidget(self.search_edit)
        self.setLayout(layout)

    def setup_connections(self) -> None:
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
