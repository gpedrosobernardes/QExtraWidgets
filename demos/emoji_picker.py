import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, 
                               QLineEdit, QHBoxLayout, QFormLayout, QSpinBox, 
                               QCheckBox, QGroupBox, QPushButton, QComboBox,
                               QDoubleSpinBox)

from qextrawidgets.emoji_utils import EmojiImageProvider
from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.utils import QEmojiFonts
from qextrawidgets.widgets.emoji_picker import QEmojiPicker
from qextrawidgets.items.emoji_category_item import QEmojiCategoryItem
from qextrawidgets.items.emoji_item import QEmojiItem
from emoji_data_python import emoji_data
from functools import partial


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("QEmojiPicker Demo")
        self.resize(800, 600)
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

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
        
        self.emoji_size_spin = QSpinBox()
        self.emoji_size_spin.setRange(16, 128)
        self.emoji_size_spin.setValue(40)
        self.emoji_size_spin.valueChanged.connect(self._on_emoji_size_changed)
        config_form.addRow("Emoji Size:", self.emoji_size_spin)

        # Emoji margin control (percentage: 0.10 - 0.50)
        self.emoji_margin_spin = QDoubleSpinBox()
        self.emoji_margin_spin.setRange(0.10, 0.50)
        self.emoji_margin_spin.setSingleStep(0.01)
        self.emoji_margin_spin.setDecimals(2)
        self.emoji_margin_spin.setValue(0.10)
        self.emoji_margin_spin.valueChanged.connect(self._on_emoji_margin_changed)
        config_form.addRow("Emoji Internal Margin:", self.emoji_margin_spin)

        # Grid spacing control
        self.grid_spacing_spin = QSpinBox()
        self.grid_spacing_spin.setRange(0, 50)
        self.grid_spacing_spin.setValue(8)
        self.grid_spacing_spin.valueChanged.connect(self._on_grid_spacing_changed)
        config_form.addRow("Grid Spacing:", self.grid_spacing_spin)

        self.favorite_check = QCheckBox()
        self.favorite_check.setChecked(True)
        self.favorite_check.stateChanged.connect(self._on_favorite_changed)
        config_form.addRow("Show Favorites:", self.favorite_check)

        self.recent_check = QCheckBox()
        self.recent_check.setChecked(True)
        self.recent_check.stateChanged.connect(self._on_recent_changed)
        config_form.addRow("Show Recents:", self.recent_check)

        self.font_combo = QComboBox()
        self.font_combo.addItem(QEmojiFonts.loadTwemojiFont())
        self.font_combo.currentTextChanged.connect(self._on_font_combo_changed)
        config_form.addRow("Emoji Font:", self.font_combo)

        self.use_pixmaps_check = QCheckBox()
        self.use_pixmaps_check.setChecked(True)
        self.use_pixmaps_check.stateChanged.connect(self._on_use_pixmaps_changed)
        config_form.addRow("Use Pixmaps:", self.use_pixmaps_check)

        controls_layout.addWidget(config_group)

        # Categories Group
        cat_group = QGroupBox("Custom Categories")
        cat_layout = QVBoxLayout(cat_group)
        
        self.add_cat_btn = QPushButton("Add 'Custom' Category")
        self.add_cat_btn.clicked.connect(self._add_custom_category)
        cat_layout.addWidget(self.add_cat_btn)

        self.remove_cat_btn = QPushButton("Remove 'Custom' Category")
        self.remove_cat_btn.setEnabled(False)
        self.remove_cat_btn.clicked.connect(self._remove_custom_category)
        cat_layout.addWidget(self.remove_cat_btn)

        controls_layout.addWidget(cat_group)
        controls_layout.addStretch()

        # Output Area
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        self.line_edit = QLineEdit()
        self.line_edit.setFont(QEmojiFonts.twemojiFont())
        self.line_edit.setPlaceholderText("Picked emojis will appear here...")
        output_layout.addWidget(self.line_edit)
        controls_layout.addWidget(output_group)

        # Right side: Emoji Picker
        self.emoji_picker = QEmojiPicker()
        self.emoji_picker.picked.connect(self._on_emoji_picked)
        # Ensure the picker's margin matches the UI initial value
        self.emoji_picker.delegate().setItemInternalMargin(self.emoji_margin_spin.value())

        # Setup initial state based on configuration
        self._on_use_pixmaps_changed(self.use_pixmaps_check.checkState().value)

        main_layout.addWidget(self.emoji_picker, 2)

    def _on_emoji_picked(self, emoji: str) -> None:
        self.line_edit.insert(emoji)

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

    def _on_favorite_changed(self, state: int) -> None:
        # Dynamic toggling of favorite category is not yet supported in the model
        pass
        # self.emoji_picker.model().setFavoriteCategory(state == Qt.CheckState.Checked.value)

    def _on_recent_changed(self, state: int) -> None:
        # Dynamic toggling of recent category is not yet supported in the model
        pass
        # self.emoji_picker.model().setRecentCategory(state == Qt.CheckState.Checked.value)

    def _on_font_combo_changed(self, font_family: str) -> None:
        font = QFont(font_family)
        # setEmojiPixmapGetter handles font families
        self.emoji_picker.setEmojiPixmapGetter(font_family)
        self.line_edit.setFont(font)

    def _on_use_pixmaps_changed(self, state: int) -> None:
        if state == Qt.CheckState.Checked.value:
            self.emoji_picker.setEmojiPixmapGetter(partial(EmojiImageProvider.getPixmap, margin=0, size=64, dpr=1.0))
        else:
            # Revert to current font in combo
            self.emoji_picker.setEmojiPixmapGetter(self.font_combo.currentText())

    def _add_custom_category(self) -> None:
        icon = QThemeResponsiveIcon.fromAwesome("fa6s.rocket")
        category_item = QEmojiCategoryItem("Custom", icon)
        self.emoji_picker.model().appendRow(category_item)
        
        # Add some sample emojis (using first 10 from data)
        items = [QEmojiItem(emoji_data[i]) for i in range(10)]
        category_item.appendRows(items)
        
        self.add_cat_btn.setEnabled(False)
        self.remove_cat_btn.setEnabled(True)

    def _remove_custom_category(self) -> None:
        index = self.emoji_picker.model().findCategory("Custom")
        if index:
            self.emoji_picker.model().removeRow(index.row())
            
        self.add_cat_btn.setEnabled(True)
        self.remove_cat_btn.setEnabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
