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
import unicodedata

from PySide6.QtCore import Qt, QSortFilterProxyModel, QModelIndex
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

from qextrawidgets.core.utils.emojis import QEmojiImageProvider
from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.gui.proxys import QDecorationRoleProxyModel
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
        self._category_filter: str = ""  # "" = all

    def setCategory(self, category: str) -> None:
        self._category_filter = category if category != "All" else ""
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        index = self.sourceModel().index(source_row, 0, source_parent)

        # Category filter
        if self._category_filter:
            if index.data(CATEGORY_ROLE) != self._category_filter:
                return False

        # Text filter (search in emoji character via EditRole)
        pattern = self.filterRegularExpression().pattern()
        if pattern:
            emoji = index.data(Qt.ItemDataRole.EditRole) or ""
            if pattern.lower() not in emoji.lower():
                return False

        return True


# ---------------------------------------------------------------------------
# Example data — subset of emojis grouped by category
# ---------------------------------------------------------------------------

EMOJI_CATEGORIES: dict[str, list[str]] = {
    "Smileys": [
        "😀", "😁", "😂", "🤣", "😃", "😄", "😅", "😆", "😇", "😈",
        "😉", "😊", "😋", "😌", "😍", "🥰", "😎", "🤓", "🧐", "😏",
        "😒", "😞", "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫",
        "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬", "🤯", "😳",
        "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗", "🤔", "🤭",
        "🤫", "🤥", "😶", "😐", "😑", "😬", "🙄", "😯", "😦", "😧",
        "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐", "🥴", "🤢",
        "🤮", "🤧", "😷", "🤒", "🤕",
    ],
    "Gestures": [
        "👋", "🤚", "🖐️", "✋", "🖖", "👌", "🤌", "🤏", "✌️", "🤞",
        "🤟", "🤘", "🤙", "👈", "👉", "👆", "🖕", "👇", "☝️", "👍",
        "👎", "✊", "👊", "🤛", "🤜", "👏", "🙌", "👐", "🤲", "🤝",
        "🙏", "✍️", "💅", "🤳", "💪", "🦾", "🦿", "🦵", "🦶",
    ],
    "Animals": [
        "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐻‍❄️", "🐨",
        "🐯", "🦁", "🐮", "🐷", "🐸", "🐵", "🙈", "🙉", "🙊", "🐔",
        "🐧", "🐦", "🐤", "🦆", "🦅", "🦉", "🦇", "🐺", "🐗", "🐴",
        "🦄", "🐝", "🪱", "🐛", "🦋", "🐌", "🐞", "🐜", "🪲", "🦟",
        "🦗", "🪰", "🦂", "🐢", "🐍", "🦎", "🦖", "🦕", "🐊", "🐸",
        "🦓", "🦍", "🦧", "🦣", "🐘", "🦛", "🦏", "🐪", "🐫", "🦒",
        "🦘", "🦬", "🐃", "🐂", "🐄", "🐎", "🐖", "🐏", "🐑", "🦙",
        "🐐", "🦌", "🐕", "🐩", "🦮", "🐕‍🦺", "🐈", "🐈‍⬛", "🐓", "🦃",
    ],
    "Food": [
        "🍎", "🍊", "🍋", "🍇", "🍓", "🫐", "🍈", "🍒", "🍑", "🥭",
        "🍍", "🥥", "🥝", "🍅", "🍆", "🥑", "🫑", "🥦", "🥬", "🥒",
        "🌽", "🥕", "🧄", "🧅", "🥔", "🍠", "🧇", "🥞", "🧈", "🍳",
        "🥚", "🧀", "🥗", "🥙", "🌮", "🌯", "🥪", "🍕", "🍔", "🍟",
        "🌭", "🍿", "🍦", "🍧", "🍨", "🍩", "🍪", "🎂", "🍰", "🧁",
        "🍫", "🍬", "🍭", "☕", "🍵", "🧃", "🥤", "🧋", "🍺", "🍻",
    ],
    "Objects": [
        "⌚", "📱", "💻", "⌨️", "🖥️", "🖨️", "🖱️", "📷", "📸", "📹",
        "🎥", "📞", "☎️", "📟", "📠", "📺", "📻", "🧭", "⏱️", "⏰",
        "📡", "🔋", "🔌", "💡", "🔦", "🕯️", "🪔", "🧯", "🛢️", "💰",
        "💳", "🪙", "💎", "⚖️", "🔧", "🔨", "⚒️", "🛠️", "🔩", "⚙️",
        "🔗", "⛓️", "🧲", "🔫", "💣", "🪓", "🔪", "🗡️", "⚔️", "🛡️",
        "🚪", "🪞", "🪟", "🛋️", "🪑", "🚽", "🧻", "🚿", "🛁",
    ],
    "Symbols": [
        "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔",
        "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "✨", "⭐",
        "🌟", "💫", "⚡", "🌈", "🔥", "💧", "❄️", "🌊", "💥", "🎉",
        "🎊", "🎈", "🎁", "🏆", "🥇", "🥈", "🥉", "🎯", "🎮", "🎲",
        "♠️", "♥️", "♦️", "♣️", "🃏", "🀄", "♟️", "✅", "❌", "⭕",
        "🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "⚫", "⚪", "🟤",
    ],
}

ALL_CATEGORIES = ["All"] + list(EMOJI_CATEGORIES.keys())


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class EmojiDemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QEmojiView Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))
        self.resize(800, 620)

        # ------------------------------------------------------------------
        # Model chain:
        #   QStandardItemModel
        #       -> EmojiFilterProxyModel
        #           -> QDecorationRoleProxyModel  <- passed to QEmojiView
        #
        # QDecorationRoleProxyModel is NOT created internally by
        # QEmojiView in this flow — it is constructed here so we can
        # chain the filter proxy before it, without losing the separation of
        # concerns (the decoration proxy never touches the source model).
        # ------------------------------------------------------------------
        self._source_model = QStandardItemModel()
        self._build_model()

        self._filter_proxy = EmojiFilterProxyModel()
        self._filter_proxy.setSourceModel(self._source_model)

        self._decoration_proxy = QDecorationRoleProxyModel()
        self._decoration_proxy.setSourceModel(self._filter_proxy)

        self.init_widgets()
        self.init_layout()
        self.init_connections()

        self._on_size_changed(48)

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
        self._source_combo.addItems(["PNG (Twemoji)", "SVG (Twemoji)", "System font"])

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
        self._emoji_view = QEmojiView()
        self._emoji_view.setModel(self._decoration_proxy)
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
        self._emoji_view.itemClicked.connect(self._on_item_clicked)

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
        for category, emojis in EMOJI_CATEGORIES.items():
            for emoji in emojis:
                item = QStandardItem()
                item.setEditable(False)
                item.setData(emoji, Qt.ItemDataRole.EditRole)
                item.setData(category, CATEGORY_ROLE)
                try:
                    name = unicodedata.name(emoji[0], emoji)
                except (ValueError, TypeError):
                    name = emoji
                item.setToolTip(f"{emoji}  {name}")
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
        provider = getattr(self._emoji_view, "_emoji_image_provider", None)
        if provider is None:
            return
        sources = ["png", "svg", "Segoe UI Emoji"]
        provider.setSource(sources[index])

    def _on_size_changed(self, value: int) -> None:
        from PySide6.QtCore import QSize
        self._size_label.setText(f"{value} px")
        self._emoji_view.setIconSize(QSize(value, value))

    def _on_item_clicked(self, index: QModelIndex) -> None:
        """Displays details of the clicked emoji.

        The received index points to the QDecorationRoleProxyModel.
        It is necessary to map two levels down to the QStandardItemModel to
        read the data directly.
        """
        # decoration proxy -> filter proxy -> source model
        filter_index = self._decoration_proxy.mapToSource(index)
        source_index = self._filter_proxy.mapToSource(filter_index)

        emoji = source_index.data(Qt.ItemDataRole.EditRole)
        if not emoji:
            return

        pixmap_image_provider = self._emoji_view.emojiImageProvider()

        if pixmap_image_provider is None:
            return

        size = self._preview_label.size().height()
        dpr = self._preview_label.devicePixelRatio()
        pixmap = QEmojiImageProvider.getPixmapBy(emoji, size, dpr, pixmap_image_provider.getSource())

        self._selected_emoji = emoji
        self._preview_label.setPixmap(pixmap)

        codepoints = " ".join(f"U+{ord(c):04X}" for c in emoji if c != "\uFE0F")
        self._codepoint_label.setText(f"Codepoints: {codepoints}")

        try:
            name = unicodedata.name(emoji[0])
        except (ValueError, TypeError):
            name = "—"
        self._name_label.setText(f"Name: {name}")
        self._char_label.setText(emoji)
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
    # logger = logging.getLogger(f"qextrawidgets.widgets.views.emoji_view.QEmojiView._on_request_image")
    logger = logging.getLogger(f"qextrawidgets.widgets.views.grid_icon_view.QEmojiView.paintEvent")
    logger.setLevel(logging.DEBUG)

    app = QApplication(sys.argv)
    app.setApplicationName("QEmojiView Demo")
    app.setStyle("Fusion")

    window = EmojiDemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()