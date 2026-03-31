import logging
import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QHBoxLayout, QGroupBox, QVBoxLayout, QFormLayout, QSpinBox, QDoubleSpinBox, QLineEdit, )

from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.widgets.miscellaneous.awesome_picker import QAwesomePicker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("QEmojiPicker Demo")
        self.resize(800, 600)
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        self._init_widgets()
        self.setup_layout()
        self.setup_connections()

    def _init_widgets(self) -> None:
        # Picker Configuration Widgets
        self.awesome_picker = QAwesomePicker()

        emoji_picker_view = self.awesome_picker.view()
        emoji_picker_delegate = self.awesome_picker.delegate()

        self.icon_size_spin = QSpinBox()
        self.icon_size_spin.setRange(16, 128)
        self.icon_size_spin.setValue(emoji_picker_view.iconSize().width())

        self.icon_margin_spin = QDoubleSpinBox()
        self.icon_margin_spin.setRange(0.10, 0.50)
        self.icon_margin_spin.setSingleStep(0.01)
        self.icon_margin_spin.setDecimals(2)
        self.icon_margin_spin.setValue(emoji_picker_delegate.itemInternalMargin())

        self.grid_spacing_spin = QSpinBox()
        self.grid_spacing_spin.setRange(0, 50)
        self.grid_spacing_spin.setValue(emoji_picker_view.margin())

        # Input Widgets
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Type a message...")

    def setup_connections(self) -> None:
        self.icon_size_spin.valueChanged.connect(self._on_icon_size_changed)
        self.icon_margin_spin.valueChanged.connect(self._on_icon_margin_changed)
        self.grid_spacing_spin.valueChanged.connect(self._on_grid_spacing_changed)

    def setup_layout(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Left side: Controls
        controls_container = QWidget()
        controls_layout = QVBoxLayout(controls_container)
        main_layout.addWidget(controls_container, 1)

        # Picker Configuration Group
        config_group = QGroupBox("Configuration")
        config_form = QFormLayout(config_group)

        config_form.addRow("Icon Size:", self.icon_size_spin)
        config_form.addRow("Icon Internal Margin:", self.icon_margin_spin)
        config_form.addRow("Grid Spacing:", self.grid_spacing_spin)

        controls_layout.addWidget(config_group)

        # Right side: Playground
        playground_container = QGroupBox("Playground")
        playground_layout = QVBoxLayout(playground_container)

        main_layout.addWidget(playground_container, 2)

        # Add a spacer or label
        playground_layout.addWidget(self.awesome_picker)

    def _on_icon_size_changed(self, value: int) -> None:
        self.awesome_picker.view().setIconSize(QSize(value, value))

    def _on_icon_margin_changed(self, value: float) -> None:
        """Handle emoji margin changes from the UI.

        Args:
            value (float): Margin percentage value between 0.10 and 0.50.
        """
        # Forward the percentage value to the picker
        self.awesome_picker.delegate().setItemInternalMargin(value)

    def _on_grid_spacing_changed(self, value: int) -> None:
        self.awesome_picker.view().setMargin(value)


if __name__ == "__main__":
    logs_folder = Path("../logs")
    logs_folder.mkdir(parents=True, exist_ok=True)

    file_name = datetime.now().strftime("../logs/log_%Y-%m-%d.log")

    # logger = logging.getLogger(f"qextrawidgets.widgets.views.grouped_icon_view.QGroupedIconView.indexAt")
    # logger.setLevel(logging.DEBUG)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
