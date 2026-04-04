import logging

from PySide6.QtGui import QFontDatabase, QShortcut, QKeySequence
import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QHBoxLayout,
    QFormLayout,
    QSpinBox,
    QCheckBox,
    QGroupBox,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
    QToolButton,
    QLabel,
)

from qextrawidgets.core.utils import QSystemUtils
from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.core.utils.emoji_fonts import QEmojiFonts
from qextrawidgets.gui.items.icon_item import QIconItem
from qextrawidgets.widgets.menus.emoji_picker_menu import QEmojiPickerMenu
from qextrawidgets.gui.items import QIconCategoryItem

from emoji_data_python import emoji_data


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("QEmojiPicker Demo")
        self.resize(800, 600)
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        self._init_widgets()
        self.setup_layout()
        self.setup_connections()
        self.setup_initial_state()

    def _init_widgets(self) -> None:
        # Picker Configuration Widgets
        self.emoji_picker_menu = QEmojiPickerMenu(self)
        self.emoji_picker = self.emoji_picker_menu.picker()

        emoji_picker_view = self.emoji_picker.view()
        emoji_picker_delegate = self.emoji_picker.delegate()

        self.emoji_btn = QToolButton()
        self.emoji_btn.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.face-smile"))
        self.emoji_btn.setMenu(self.emoji_picker_menu)
        self.emoji_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.emoji_size_spin = QSpinBox()
        self.emoji_size_spin.setRange(16, 128)
        self.emoji_size_spin.setSingleStep(5)
        self.emoji_size_spin.setValue(emoji_picker_view.iconSize().width())

        self.emoji_margin_spin = QDoubleSpinBox()
        self.emoji_margin_spin.setRange(0.10, 0.50)
        self.emoji_margin_spin.setSingleStep(0.05)
        self.emoji_margin_spin.setDecimals(2)
        self.emoji_margin_spin.setValue(emoji_picker_delegate.itemInternalMargin())

        self.grid_spacing_spin = QSpinBox()
        self.grid_spacing_spin.setRange(0, 50)
        self.grid_spacing_spin.setSingleStep(5)
        self.grid_spacing_spin.setValue(emoji_picker_view.margin())

        self.use_pixmaps_check = QCheckBox()
        self.use_pixmaps_check.setChecked(True)

        self.font_combo = QComboBox()
        self.font_combo.addItems(self._get_emoji_fonts())

        # Category Widgets
        self.add_cat_btn = QPushButton("Add 'Custom' Category")

        self.remove_cat_btn = QPushButton("Remove 'Custom' Category")
        self.remove_cat_btn.setEnabled(False)

        # Input Widgets
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Type a message...")

    def setup_connections(self) -> None:
        self.emoji_picker.picked.connect(self._on_emoji_picked)
        self.emoji_size_spin.valueChanged.connect(self._on_emoji_size_changed)
        self.emoji_margin_spin.valueChanged.connect(self._on_emoji_margin_changed)
        self.grid_spacing_spin.valueChanged.connect(self._on_grid_spacing_changed)
        self.font_combo.currentTextChanged.connect(self._on_font_combo_changed)
        self.use_pixmaps_check.stateChanged.connect(self._on_use_pixmap_changed)
        self.add_cat_btn.clicked.connect(self._add_custom_category)
        self.remove_cat_btn.clicked.connect(self._remove_custom_category)

        obs_shortcut = QShortcut(QKeySequence("F12"), self)
        obs_shortcut.activated.connect(lambda: print(QSystemUtils.getObsRect(self)))

    def setup_initial_state(self) -> None:
        self._on_use_pixmap_changed(self.use_pixmaps_check.checkState())

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

        config_form.addRow("Emoji Size:", self.emoji_size_spin)
        config_form.addRow("Emoji Internal Margin:", self.emoji_margin_spin)
        config_form.addRow("Grid Spacing:", self.grid_spacing_spin)

        controls_layout.addWidget(config_group)

        # Source group
        source_group = QGroupBox("Source")
        source_form = QFormLayout(source_group)
        source_form.addRow("Use Pixmaps:", self.use_pixmaps_check)
        source_form.addRow("Emoji Font:", self.font_combo)

        controls_layout.addWidget(source_group)

        # Categories Group
        cat_group = QGroupBox("Custom Categories")
        cat_layout = QVBoxLayout(cat_group)

        cat_layout.addWidget(self.add_cat_btn)
        cat_layout.addWidget(self.remove_cat_btn)

        controls_layout.addWidget(cat_group)
        controls_layout.addStretch()

        # Right side: Playground
        playground_container = QGroupBox("Playground")
        playground_layout = QVBoxLayout(playground_container)

        main_layout.addWidget(playground_container, 2)

        # Add a spacer or label
        playground_layout.addStretch()
        playground_layout.addWidget(QLabel("Type a message:"))

        # Input Row
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)

        input_layout.addWidget(self.emoji_btn)
        input_layout.addWidget(self.line_edit)

        playground_layout.addWidget(input_container)

    def _on_emoji_picked(self, item: QIconItem) -> None:
        self.line_edit.insert(self.emoji_picker.resolveEmojiColorByIcon(item))

    def _on_emoji_size_changed(self, value: int) -> None:
        self.emoji_picker.view().setIconSize(QSize(value, value))

    def _on_emoji_margin_changed(self, value: float) -> None:
        """Handle emoji margin changes from the UI.

        Args:
            value (float): Margin percentage value between 0.10 and 0.50.
        """
        # Forward the percentage value to the picker
        self.emoji_picker.delegate().setItemInternalMargin(value)

    def _on_grid_spacing_changed(self, value: int) -> None:
        self.emoji_picker.view().setMargin(value)

    def _on_font_combo_changed(self, font_family: str) -> None:
        self.emoji_picker.setIconPixmapGetter(
            lambda icon: self.emoji_picker.fontEmojiPixmapGetter(font_family, icon))
        QFontDatabase.setApplicationEmojiFontFamilies([font_family])
        self.line_edit.setFont(QApplication.font())

    def _on_use_pixmap_changed(self, state: Qt.CheckState) -> None:
        if Qt.CheckState(state) == Qt.CheckState.Checked:
            self.font_combo.setDisabled(True)
            self.emoji_picker.setIconPixmapGetter(self.emoji_picker.emojiPixmapGetter)
            QFontDatabase.setApplicationEmojiFontFamilies(["Twemoji"])
            self.line_edit.setFont("Twemoji")
        else:
            # Revert to current font in combo
            self.font_combo.setDisabled(False)
            self._on_font_combo_changed(self.font_combo.currentText())

    def _add_custom_category(self) -> None:
        icon = QThemeResponsiveIcon.fromAwesome("fa6s.rocket")
        category_item = QIconCategoryItem("Custom", "Custom", icon)
        self.emoji_picker.model().appendRow(category_item)

        # Add some sample emojis (using first 10 from data)
        items = [QIconItem.fromEmojiChar(emoji_data[i]) for i in range(10)]
        category_item.appendRows(items)

        self.add_cat_btn.setEnabled(False)
        self.remove_cat_btn.setEnabled(True)

    def _remove_custom_category(self) -> None:
        index = self.emoji_picker.model().findCategory("Custom")
        if index:
            self.emoji_picker.model().removeRow(index.row())

        self.add_cat_btn.setEnabled(True)
        self.remove_cat_btn.setEnabled(False)

    @staticmethod
    def _get_emoji_fonts():
        all_fonts = set(QFontDatabase.families())
        emoji_fonts = {"DejaVu Sans", "Noto Color Emoji"}

        supported_emoji_fonts = list(all_fonts.intersection(emoji_fonts))
        twemoji_font = QEmojiFonts.loadTwemojiFont()
        supported_emoji_fonts.append(twemoji_font)

        return supported_emoji_fonts


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(100, 500, 800, 600)
    window.show()
    sys.exit(app.exec())
