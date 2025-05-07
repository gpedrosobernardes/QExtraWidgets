import logging
import time
import typing

from PySide6.QtCore import QSize, Qt, Signal, QModelIndex, QPoint
from PySide6.QtGui import QStandardItemModel, QStandardItem, QMouseEvent, QImageReader, QPixmap
from PySide6.QtWidgets import QListView, QSizePolicy, QAbstractScrollArea
from emojis.db import Emoji

from extra_qwidgets.abc_widgets.emoji_picker.emoji_sort_filter_proxy_model import EmojiSortFilterProxyModel
from extra_qwidgets.utils import get_emoji_path


class QEmojiGrid(QListView):
    mouseEnteredEmoji = Signal(Emoji)
    mouseLeftEmoji = Signal()
    emojiClicked = Signal(Emoji)
    contextMenu = Signal(Emoji, QPoint)

    def __init__(self, icon_size: QSize = QSize(36, 36), grid_size: QSize = QSize(40, 40)):
        super().__init__()
        self.model = QStandardItemModel()
        self._proxy = EmojiSortFilterProxyModel(self)
        self._proxy.setSourceModel(self.model)
        self.setModel(self._proxy)
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setUniformItemSizes(True)
        self.setWrapping(True)
        self.setIconSize(icon_size)
        self.setGridSize(grid_size)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._setup_binds()

    def add_emoji(self, emoji: Emoji) -> QStandardItem:
        t0 = time.perf_counter()
        reader = QImageReader(get_emoji_path(emoji))
        reader.setScaledSize(self.iconSize())
        image = reader.read()
        pixmap = QPixmap.fromImage(image)
        t1 = time.perf_counter()
        logging.debug(f"Time to load emoji {emoji.emoji} icon: {t1 - t0:.4f} seconds")
        item = QStandardItem()
        item.setData(emoji, Qt.ItemDataRole.UserRole)
        item.setIcon(pixmap)
        self.addItem(item)
        return item

    def _setup_binds(self):
        self.setMouseTracking(True)
        self.mouseMoveEvent = lambda event: self._on_mouse_enter_emoji_grid(event)
        self.clicked.connect(self.__on_clicked)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def __on_clicked(self, index: QModelIndex):
        item_data = self.proxy().itemData(index)[Qt.ItemDataRole.UserRole]
        self.emojiClicked.emit(item_data)

    def _on_mouse_enter_emoji_grid(self, event: QMouseEvent):
        index = self.indexAt(event.pos())
        if index.isValid():
            item_data = self.proxy().itemData(index)[Qt.ItemDataRole.UserRole]
            self.mouseEnteredEmoji.emit(item_data)
        else:
            self.mouseLeftEmoji.emit()

    def _on_context_menu(self, pos: QPoint):
        index = self.indexAt(pos)
        if index.isValid():
            item_data = self.proxy().itemData(index)[Qt.ItemDataRole.UserRole]
            self.contextMenu.emit(item_data, self.mapToGlobal(pos))

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
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == emoji:
                return item
        return None

    def allFiltered(self) -> bool:
        return self._proxy.rowCount() == 0

    def isEmpty(self) -> bool:
        return self.model.rowCount() == 0

    def filter(self, text: str):
        self._proxy.setFilterFixedString(text)
        self._adjust_fixed_height()

    def proxy(self) -> EmojiSortFilterProxyModel:
        return self._proxy