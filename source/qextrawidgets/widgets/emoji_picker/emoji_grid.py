import typing
from enum import Enum

from PySide6.QtCore import QSize, Qt, Signal, QPoint, QEvent, QAbstractProxyModel
from PySide6.QtGui import QStandardItemModel, QStandardItem, QMouseEvent
from PySide6.QtWidgets import QListView, QAbstractScrollArea, QSizePolicy
from emojis.db import Emoji

from qextrawidgets.proxys.emoji_sort_filter import EmojiSortFilterProxyModel
from qextrawidgets.widgets.emoji_picker.emoji_delegate import EmojiDelegate


class QEmojiGrid(QListView):
    # Signals
    mouseEnteredEmoji = Signal(Emoji, QStandardItem)  # object = Emoji
    mouseLeftEmoji = Signal(Emoji, QStandardItem)
    emojiClicked = Signal(Emoji, QStandardItem)
    contextMenu = Signal(Emoji, QStandardItem, QPoint)

    class LimitTreatment(int, Enum):
        RemoveFirstOne = 1
        RemoveLastOne = 2

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__model = QStandardItemModel(self)

        # Assuming you have the Proxy imported or defined
        self.__last_index = None
        self.__limit = float("inf")
        self.__limit_treatment = None
        self.__proxy = EmojiSortFilterProxyModel(self)
        self.__proxy.setSourceModel(self.__model)
        self.setModel(self.__proxy)

        self.setMouseTracking(True)  # Essential for hover to work
        self.setIconSize(QSize(36, 36))
        self.setGridSize(QSize(40, 40))

        # Performance configuration
        self.setItemDelegate(EmojiDelegate(self))

        # Default settings
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setUniformItemSizes(True)
        self.setWrapping(True)
        self.setDragEnabled(False)

        # Turn off scroll bars (parent should scroll)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Size policy: Expands horizontally, Fixed vertically (based on sizeHint)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)

        # Native adjustment (helps, but sizeHint does the heavy lifting)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

    def sizeHint(self) -> QSize:
        """
        Tells the parent Layout the ideal size of this widget.
        Qt calls this automatically when the layout is invalidated.
        """
        if self.model() is None or self.model().rowCount() == 0:
            return QSize(0, 0)

        # Available width (if widget hasn't been shown yet, use a default value)
        width = self.width() if self.width() > 0 else 400

        # Grid dimensions
        grid_sz = self.gridSize()
        if grid_sz.isEmpty():
            grid_sz = QSize(40, 40)  # Fallback

        # Mathematical calculation
        item_width = grid_sz.width()
        item_height = grid_sz.height()

        # How many fit per row?
        items_per_row = max(1, width // item_width)

        # How many rows do we need?
        total_items = self.model().rowCount()
        rows = (total_items + items_per_row - 1) // items_per_row  # Ceil division

        height = rows * item_height + 5  # +5 safety padding

        return QSize(width, height)

    def resizeEvent(self, event):
        """
        When width changes, the number of rows changes.
        We need to notify the layout to read sizeHint() again.
        """
        super().resizeEvent(event)
        self.updateGeometry()

    # --- Events (standard Python/Qt snake_case) ---

    def mouseMoveEvent(self, e: QMouseEvent):
        """Manages mouse entry/exit detection on items."""
        super().mouseMoveEvent(e)

        index = self.indexAt(e.pos())

        # If mouse left a valid item or entered void
        if self.__last_index and (not index.isValid() or index != self.__last_index):
            item = self.__get_item_from_index(self.__last_index)
            if item:
                emoji = item.data(Qt.ItemDataRole.UserRole)
                self.mouseLeftEmoji.emit(emoji, item)
            self.__last_index = None

        # If mouse entered a new item
        if index.isValid() and index != self.__last_index:
            self.__last_index = index
            item = self.__get_item_from_index(index)
            if item:
                emoji = item.data(Qt.ItemDataRole.UserRole)
                self.mouseEnteredEmoji.emit(emoji, item)

    def leaveEvent(self, e: QEvent):
        """Ensures exit signal is emitted when leaving the widget."""
        if self.__last_index:
            item = self.__get_item_from_index(self.__last_index)
            if item:
                emoji = item.data(Qt.ItemDataRole.UserRole)
                self.mouseLeftEmoji.emit(emoji, item)
            self.__last_index = None
        super().leaveEvent(e)

    def mouseReleaseEvent(self, e: QMouseEvent):
        """Manages click."""
        super().mouseReleaseEvent(e)
        if e.button() == Qt.MouseButton.LeftButton:
            index = self.indexAt(e.pos())
            if index.isValid():
                item = self.__get_item_from_index(index)
                emoji = item.data(Qt.ItemDataRole.UserRole)
                self.emojiClicked.emit(emoji, item)

    def contextMenuEvent(self, e):
        """Manages context menu."""
        index = self.indexAt(e.pos())
        if index.isValid():
            item = self.__get_item_from_index(index)
            emoji = item.data(Qt.ItemDataRole.UserRole)
            self.contextMenu.emit(emoji, item, self.mapToGlobal(e.pos()))

    # --- Private Helper Methods ---

    def __get_item_from_index(self, index):
        # If using proxy, needs mapping
        if isinstance(index.model(), QAbstractProxyModel):
            index = self.__proxy.mapToSource(index)
        return self.__model.itemFromIndex(index)

    @staticmethod
    def _create_emoji_item(emoji: Emoji) -> QStandardItem:
        item = QStandardItem()
        item.setData(emoji, Qt.ItemDataRole.UserRole)
        item.setEditable(False)
        return item

    def __treat_limit(self):
        if self.__limit_treatment == self.LimitTreatment.RemoveFirstOne:
            self.__model.removeRow(0)
        elif self.__limit_treatment == self.LimitTreatment.RemoveLastOne:
            self.__model.removeRow(self.__model.rowCount() - 1)

    # --- Public API (camelCase) ---
    def addEmoji(self, emoji: Emoji, update_geometry: bool = True):
        """Adds an item to the model."""
        if self.__model.rowCount() + 1 > self.__limit:
            self.__treat_limit()

        if self.__model.rowCount() < self.__limit:
            self.__model.appendRow(self._create_emoji_item(emoji))
            # Calls height adjustment after adding (can be optimized to call only once at the end)
            if update_geometry:
                self.updateGeometry()

    def emojiItem(self, emoji: Emoji) -> typing.Optional[QStandardItem]:
        start_index = self.__model.index(0, 0)
        matches = self.__model.match(start_index, Qt.ItemDataRole.UserRole, emoji, 1, Qt.MatchFlag.MatchExactly)
        if matches:
            return matches[0]
        return None

    def removeEmoji(self, emoji: Emoji, update_geometry: bool = True):
        """Removes a specific emoji."""
        # Search logic depends on how data is stored.
        # Simple example iterating (slow for many items, ideal would be a mapping dict)
        match = self.emojiItem(emoji)
        if match:
            self.__model.removeRow(match.row())
            if update_geometry:
                self.updateGeometry()

    def allFiltered(self) -> bool:
        """Returns True if all items are filtered (hidden by Proxy)."""
        return self.__proxy.rowCount() == 0

    def filterContent(self, text: str):
        """Applies filter."""
        self.__proxy.setFilterFixedString(text)
        self.updateGeometry() # Readjusts height based on what's left

    def setLimit(self, limit: int):
        self.__limit = limit

    def limit(self):
        return self.__limit

    def setLimitTreatment(self, limit_treatment: typing.Optional[LimitTreatment]):
        self.__limit_treatment = limit_treatment

    def limitTreatment(self) -> LimitTreatment:
        return self.__limit_treatment
