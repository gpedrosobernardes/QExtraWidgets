"""
demo_emoji_view.py
==================
Interactive demo for QEmojiView.

Demonstrated Features:
- Emoji grid display via QEmojiView
- Real-time text filtering (searching EditRole)
- Category filtering (via custom QSortFilterProxyModel)
- Rendering source switching (PNG / SVG / System Font)
- Dynamic icon size adjustment
- Emoji selection displaying character and codepoint

Model Architecture:
    QStandardItemModel          <- Raw data (emoji + category)
        |
    EmojiFilterProxyModel       <- Filters by text and/or category
        |
    QDecorationRoleProxyModel   <- Caches pixmaps without touching the source model
        |
    QEmojiView                  <- Renders the grid

Execution:
    python demo_emoji_view.py
"""
import logging
import sys

from PySide6.QtCore import Qt, QSortFilterProxyModel, QModelIndex, QSize
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QSlider,
    QGroupBox,
    QStatusBar,
    QSizePolicy,
    QFrame,
    QToolButton,
)
from emoji_data_python import EmojiChar

from qextrawidgets.core.utils.emojis import QEmojiPixmapCache
from qextrawidgets.core.utils.emojis.emoji_utils import QEmojiUtils
from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.widgets.views import QEmojiView

# ---------------------------------------------------------------------------
# Custom category role
# ---------------------------------------------------------------------------

CATEGORY_ROLE = Qt.ItemDataRole.UserRole + 1


# ---------------------------------------------------------------------------
# Custom filter proxy — filters by text (EditRole) and category
# ---------------------------------------------------------------------------

class EmojiFilterProxyModel(QSortFilterProxyModel):
    """Filters emojis by search text and/or category.

    The text filter compares against the EditRole (emoji character).
    The category filter compares against the CATEGORY_ROLE.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._category_filter: str = ""

    def setCategory(self, category: str) -> None:
        self.beginFilterChange()
        self._category_filter = category if category != "All" else ""
        self.endFilterChange()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        index = self.sourceModel().index(source_row, 0, source_parent)

        emoji_char: EmojiChar = index.data(Qt.ItemDataRole.EditRole)

        # Category filter
        if self._category_filter:
            if emoji_char.category != self._category_filter:
                return False

        # Text filter (search in emoji character via EditRole)
        pattern = self.filterRegularExpression()
        if not pattern.match(emoji_char.name).hasMatch():
            return False

        return True


# ---------------------------------------------------------------------------
# Example data — subset of emojis grouped by category
# ---------------------------------------------------------------------------

ALL_CATEGORIES = ["All"] + list(QEmojiUtils.emojiCharPerCategory.keys())

# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class EmojiDemoWindow(QMainWindow):
    emojiFonts = ["Segoe UI Emoji", "Twemoji"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("QEmojiView Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))
        self.resize(800, 620)

        self._source_model = QStandardItemModel()
        self._build_model()

        self._filter_proxy = EmojiFilterProxyModel()
        self._filter_proxy.setSourceModel(self._source_model)

        self.init_widgets()
        self.init_layout()
        self.init_connections()

        self._on_size_changed(48)

        self._emoji_view.model().setSourceModel(self._filter_proxy)

    def init_widgets(self) -> None:
        """Instantiate and configure UI widgets."""
        self._central_widget = QWidget()
        self._controls_widget = QWidget()

        # Controls Bar Widgets
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("🔍  Search emoji…")
        self._search_edit.setClearButtonEnabled(True)

        self._category_label = QLabel("Category:")
        self._category_combo = QComboBox()
        self._category_combo.addItems(ALL_CATEGORIES)

        self._source_label = QLabel("Rendering:")
        self._source_combo = QComboBox()
        self._source_combo.addItems(["System font", "Twemoji"])

        self._size_label_title = QLabel("Size:")
        self._size_slider = QSlider(Qt.Orientation.Horizontal)
        self._size_slider.setRange(24, 96)
        self._size_slider.setValue(48)
        self._size_slider.setTickInterval(8)
        self._size_slider.setFixedWidth(120)
        self._size_label = QLabel("48 px")
        self._size_label.setFixedWidth(42)

        # Separator line
        self._sep_frame = QFrame()
        self._sep_frame.setFrameShape(QFrame.Shape.HLine)
        self._sep_frame.setFrameShadow(QFrame.Shadow.Sunken)

        # Emoji View
        # QEmojiView receives the pre-configured QDecorationRoleProxyModel.
        # Internally, the view does not create a second decoration proxy — it uses
        # whatever is passed via setModel().
        self._emoji_view = QEmojiView(self.emojiFonts[0])
        self._emoji_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Detail Panel Widgets
        self._detail_group = QGroupBox("Selected emoji")
        self._preview_label = QLabel()
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setFixedSize(72, 72)

        self._char_label = QLabel("No emoji selected")
        self._char_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self._codepoint_label = QLabel("")
        self._name_label = QLabel("")

        self._copy_btn = QToolButton()
        self._copy_btn.setText("📋 Copy")
        self._copy_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._copy_btn.setEnabled(False)

        self._selected_emoji: str = ""

        # Status Bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._update_status()

    def init_layout(self) -> None:
        """Arrange widgets into layouts and set layouts on parent widgets."""
        self.setCentralWidget(self._central_widget)
        root_layout = QVBoxLayout(self._central_widget)
        root_layout.setContentsMargins(12, 12, 12, 8)
        root_layout.setSpacing(8)

        # Controls Bar Layout
        controls_layout = QHBoxLayout(self._controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(12)
        controls_layout.addWidget(self._search_edit, stretch=3)
        controls_layout.addWidget(self._category_label)
        controls_layout.addWidget(self._category_combo, stretch=1)
        controls_layout.addWidget(self._source_label)
        controls_layout.addWidget(self._source_combo, stretch=1)
        controls_layout.addWidget(self._size_label_title)
        controls_layout.addWidget(self._size_slider)
        controls_layout.addWidget(self._size_label)

        # Main Layout assembly
        root_layout.addWidget(self._controls_widget)
        root_layout.addWidget(self._sep_frame)
        root_layout.addWidget(self._emoji_view, stretch=1)

        # Detail Panel Layout
        detail_layout = QHBoxLayout(self._detail_group)
        detail_layout.setSpacing(16)
        detail_layout.addWidget(self._preview_label)

        details_text_layout = QVBoxLayout()
        details_text_layout.addWidget(self._char_label)
        details_text_layout.addWidget(self._codepoint_label)
        details_text_layout.addWidget(self._name_label)
        details_text_layout.addStretch()
        detail_layout.addLayout(details_text_layout, stretch=1)
        detail_layout.addWidget(self._copy_btn)

        root_layout.addWidget(self._detail_group)

    def init_connections(self) -> None:
        """Connect signals to their respective slot handlers."""
        # Controls Bar Connections
        self._search_edit.textChanged.connect(self._on_search_changed)
        self._category_combo.currentTextChanged.connect(self._on_category_changed)
        self._source_combo.currentIndexChanged.connect(self._on_source_changed)
        self._size_slider.valueChanged.connect(self._on_size_changed)

        # Detail Panel & Copy Button Connections
        self._copy_btn.clicked.connect(self._on_copy_emoji)

        # Emoji View Connections
        self._emoji_view.clicked.connect(self._on_item_clicked)

        # Filter Proxy Connections
        self._filter_proxy.rowsInserted.connect(self._update_status)
        self._filter_proxy.rowsRemoved.connect(self._update_status)
        self._filter_proxy.modelReset.connect(self._update_status)

    # ------------------------------------------------------------------
    # Model
    # ------------------------------------------------------------------

    def _build_model(self) -> None:
        """Populates the QStandardItemModel with all emojis and their categories."""
        self._source_model.clear()
        for category, emoji_chars in QEmojiUtils.emojiCharPerCategory.items():
            for emoji_char in sorted(emoji_chars, key=lambda e: e.sort_order):
                item = QStandardItem()
                item.setEditable(False)
                item.setData(emoji_char, Qt.ItemDataRole.EditRole)
                item.setToolTip(f"{emoji_char.char} {emoji_char.name.title()}")
                self._source_model.appendRow(item)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_search_changed(self, text: str) -> None:
        self._filter_proxy.setFilterFixedString(text)
        self._update_status()

    def _on_category_changed(self, category: str) -> None:
        self._filter_proxy.setCategory(category)
        self._update_status()

    def _on_source_changed(self, index: int) -> None:
        font_family = self.emojiFonts[index]
        self._emoji_view.setEmojiFontFamily(font_family)

    def _on_size_changed(self, value: int) -> None:
        self._size_label.setText(f"{value} px")
        self._emoji_view.setIconSize(QSize(value, value))

    def _on_item_clicked(self, index: QModelIndex) -> None:
        """Displays details of the clicked emoji.

        The received index points to the QDecorationRoleProxyModel.
        It is necessary to map two levels down to the QStandardItemModel to
        read the data directly.
        """
        emoji_char = index.data(Qt.ItemDataRole.EditRole)
        if not emoji_char:
            return

        source_index = self._source_combo.currentIndex()
        emoji_font_family = self.emojiFonts[source_index]

        pixmap = QEmojiPixmapCache.getPixmap(emoji_font_family, emoji_char.unified)
        pixmap = pixmap.scaled(self._preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self._selected_emoji = emoji_char.char
        self._preview_label.setPixmap(pixmap)

        self._codepoint_label.setText(f"Codepoints: {emoji_char.unified}")

        self._name_label.setText(f"Name: {emoji_char.name.title()}")
        self._char_label.setText(emoji_char.char)
        self._copy_btn.setEnabled(True)

    def _on_copy_emoji(self) -> None:
        if self._selected_emoji:
            QApplication.clipboard().setText(self._selected_emoji)
            self._status.showMessage(
                f"'{self._selected_emoji}' copied to clipboard!", 2500
            )

    def _update_status(self) -> None:
        total = self._filter_proxy.rowCount()
        self._status.showMessage(f"{total} emoji(s) displayed")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)
    app.setApplicationName("QEmojiView Demo")
    app.setStyle("Fusion")

    for emoji_font_family in EmojiDemoWindow.emojiFonts:
        QEmojiPixmapCache.ensureCacheLoaded(emoji_font_family)

    window = EmojiDemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    import faulthandler

    faulthandler.enable()
    main()