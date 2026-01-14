import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, 
                               QLineEdit, QHBoxLayout, QFormLayout, QSpinBox, 
                               QCheckBox, QGroupBox, QPushButton, QComboBox)

from qextrawidgets.emoji_utils import EmojiImageProvider
from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.utils import QEmojiFonts
from qextrawidgets.widgets.emoji_picker.emoji_picker import QEmojiPicker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("QEmojiPicker Advanced Demo")
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
        
        # Setup initial state based on configuration
        self._on_use_pixmaps_changed(self.use_pixmaps_check.checkState().value)

        main_layout.addWidget(self.emoji_picker, 2)

    def _on_emoji_picked(self, emoji: str) -> None:
        self.line_edit.insert(emoji)

    def _on_emoji_size_changed(self, value: int) -> None:
        self.emoji_picker.setEmojiSize(QSize(value, value))

    def _on_favorite_changed(self, state: int) -> None:
        self.emoji_picker.setFavoriteCategory(state == Qt.CheckState.Checked.value)

    def _on_recent_changed(self, state: int) -> None:
        self.emoji_picker.setRecentCategory(state == Qt.CheckState.Checked.value)

    def _on_font_combo_changed(self, font_family: str) -> None:
        font = QFont(font_family)
        self.emoji_picker.setEmojiFont(font_family)
        self.line_edit.setFont(font)

    def _on_use_pixmaps_changed(self, state: int) -> None:
        if state == Qt.CheckState.Checked.value:
            self.emoji_picker.setEmojiPixmapGetter(
                lambda emoji, size, dpr: EmojiImageProvider.getPixmap(emoji, 0, size, dpr)
            )
        else:
            self.emoji_picker.setEmojiPixmapGetter(None)

    def _add_custom_category(self) -> None:
        icon = QThemeResponsiveIcon.fromAwesome("fa6s.rocket")
        self.emoji_picker.addCategory("Custom", "My Custom Category", icon)
        self.add_cat_btn.setEnabled(False)
        self.remove_cat_btn.setEnabled(True)

    def _remove_custom_category(self) -> None:
        self.emoji_picker.removeCategory("Custom")
        self.add_cat_btn.setEnabled(True)
        self.remove_cat_btn.setEnabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
