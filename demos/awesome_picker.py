import logging
import sys

from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QHBoxLayout,
)

from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.widgets.miscellaneous.awesome_picker import QAwesomePicker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("QtAwesomePicker Demo")
        self.resize(800, 600)
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        self._init_widgets()
        self.setup_layout()
        self.setup_connections()
        self.setup_initial_state()

    def _init_widgets(self) -> None:
        self._awesome_picker = QAwesomePicker()

    def setup_connections(self) -> None:
        pass

    def setup_initial_state(self) -> None:
        pass

    def setup_layout(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(self._awesome_picker)
        central_widget.setLayout(main_layout)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
