import typing

from PySide6.QtCore import QSize, Qt, Signal, QModelIndex, QPoint
from PySide6.QtGui import QStandardItemModel, QStandardItem, QMouseEvent
from PySide6.QtWidgets import QListView, QSizePolicy, QAbstractScrollArea
from emojis.db import Emoji

from extra_qwidgets.proxys.emoji_sort_filter import EmojiSortFilterProxyModel


class QEmojiGrid(QListView):
    mouseEnteredEmoji = Signal(Emoji, QStandardItem)
    mouseLeftEmoji = Signal(Emoji, QStandardItem)
    emojiClicked = Signal(Emoji, QStandardItem)
    contextMenu = Signal(Emoji, QStandardItem, QPoint)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = QStandardItemModel()
        self._last_emoji = None
        self._proxy = EmojiSortFilterProxyModel(self)
        self._proxy.setSourceModel(self.model)
        self.setModel(self._proxy)
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setUniformItemSizes(True)
        self.setWrapping(True)
        self.setIconSize(QSize(36, 36))
        self.setGridSize(QSize(40, 40))
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._setup_binds()

    def _setup_binds(self):
        self.setMouseTracking(True)
        self.mouseMoveEvent = lambda event: self._on_mouse_enter_emoji_grid(event)
        self.clicked.connect(self.__on_clicked)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def __on_clicked(self, index: QModelIndex):
        proxy = self.proxy()
        item_data = proxy.itemData(index)[Qt.ItemDataRole.UserRole]
        real_index = proxy.mapToSource(index)
        item = self.model.itemFromIndex(real_index)
        self.emojiClicked.emit(item_data, item)

    def _on_mouse_enter_emoji_grid(self, event: QMouseEvent):
        index = self.indexAt(event.pos())
        proxy = self.proxy()
        if index.isValid():
            item_data = proxy.itemData(index)[Qt.ItemDataRole.UserRole]
            real_index = proxy.mapToSource(index)
            item = self.model.itemFromIndex(real_index)
            args = (item_data, item)
            self.mouseEnteredEmoji.emit(*args)
            self._last_emoji = args
        elif self._last_emoji is not None:
            self.mouseLeftEmoji.emit(*self._last_emoji)

    def _on_context_menu(self, pos: QPoint):
        index = self.indexAt(pos)
        if index.isValid():
            proxy = self.proxy()
            item_data = proxy.itemData(index)[Qt.ItemDataRole.UserRole]
            item = self.model.itemFromIndex(proxy.mapToSource(index))
            self.contextMenu.emit(item_data, item, self.mapToGlobal(pos))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._adjust_fixed_height()

    def _adjust_fixed_height(self):
        itens_total = self._proxy.rowCount()
        if itens_total == 0:
            return
        item_size = self.gridSize()
        width = self.size().width()
        if item_size.width() == 0:
            return
        items_per_row = max(1, width // item_size.width())
        rows = -(-itens_total // items_per_row)
        total_height = rows * item_size.height() + 5
        self.setFixedHeight(total_height)

    def addItem(self, item: QStandardItem):
        self.model.appendRow(item)

    def removeEmoji(self, emoji: Emoji):
        item = self.getItem(emoji)
        if item:
            self.model.removeRow(item.row())

    def getItem(self, emoji: Emoji) -> typing.Optional[QStandardItem]:
        match = self.model.match(self.model.index(0, 0), Qt.ItemDataRole.UserRole, emoji, flags=Qt.MatchFlag.MatchExactly)
        return self.model.itemFromIndex(match[0]) if match else None

    def allFiltered(self) -> bool:
        return self._proxy.rowCount() == 0

    def isEmpty(self) -> bool:
        return self.model.rowCount() == 0

    def filter(self, text: str):
        self._proxy.setFilterFixedString(text)
        self._adjust_fixed_height()

    def proxy(self) -> EmojiSortFilterProxyModel:
        return self._proxy