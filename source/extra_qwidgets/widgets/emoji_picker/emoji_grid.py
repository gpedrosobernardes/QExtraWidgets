import typing

from PySide6.QtCore import QSize, Qt, Signal, QModelIndex, QPoint, QRect, QTimer
from PySide6.QtGui import QStandardItemModel, QStandardItem, QMouseEvent, QImageReader, QPixmap, QIcon
from PySide6.QtWidgets import QListView, QSizePolicy, QAbstractScrollArea, QScrollArea
from emojis.db import Emoji

from extra_qwidgets.abc_widgets.emoji_picker.emoji_sort_filter_proxy_model import EmojiSortFilterProxyModel
from extra_qwidgets.utils import get_emoji_path


class QEmojiGrid(QListView):
    mouseEnteredEmoji = Signal(Emoji)
    mouseLeftEmoji = Signal()
    emojiClicked = Signal(Emoji)
    contextMenu = Signal(Emoji, QPoint)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = QStandardItemModel()
        self._proxy = EmojiSortFilterProxyModel(self)
        self._proxy.setSourceModel(self._model)
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

    def _get_visible_rows(self, scroll_area: QScrollArea, category) -> typing.Iterable[int]:
        scroll_area_rect = scroll_area.viewport().rect()
        relative_top_left = self.mapTo(scroll_area, QPoint(0, 0))
        relative_bottom_right = self.mapTo(scroll_area, QPoint(self.width(), self.height()))
        relative_rect = QRect(relative_top_left, relative_bottom_right)
        if scroll_area_rect.intersects(relative_rect):
            top = min(self.mapFrom(scroll_area, QPoint(0, 0)).y(), 0)
            bottom = self.mapFrom(scroll_area, scroll_area_rect.bottomLeft()).y()
            item_height = self.gridSize().height()
            items_per_row = self._get_items_per_row()
            first_item = (top // item_height) * items_per_row
            last_item = (bottom // item_height + 1) * items_per_row
            return range(first_item, last_item)
        return []

    def load_visible_icons(self, scroll_area: QScrollArea, category):
        for row in self._get_visible_rows(scroll_area, category):
            item = self._model.item(row)
            if not item:
                continue
            if not item.icon().isNull():
                continue
            emoji = item.data(Qt.ItemDataRole.UserRole)
            path = get_emoji_path(emoji)
            pixmap = QPixmap(path)
            icon = QIcon(pixmap)
            item.setIcon(icon)
            src_idx = self._model.indexFromItem(item)
            proxy_idx = self._proxy.mapFromSource(src_idx)
            self._proxy.dataChanged.emit(proxy_idx, proxy_idx, [Qt.ItemDataRole.DecorationRole])

            # repaint parcial
            self.viewport().update(self.visualRect(proxy_idx))
        self._model.layoutChanged.emit()

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
        items_per_row = self._get_items_per_row()
        rows = -(-itens_total // items_per_row)
        total_height = rows * item_size.height() + 5
        self.setFixedHeight(total_height)

    def _get_items_per_row(self):
        return self.size().width() // self.gridSize().width()

    def addItem(self, item: QStandardItem):
        self._model.appendRow(item)

    def removeEmoji(self, emoji: Emoji):
        item = self.getItem(emoji)
        if item:
            self._model.removeRow(item.row())

    def getItem(self, emoji: Emoji) -> typing.Optional[QStandardItem]:
        for item in self.items():
            if item.data(Qt.ItemDataRole.UserRole) == emoji:
                return item
        return None

    def items(self) -> typing.Generator[QStandardItem]:
        for i in range(self._model.rowCount()):
            yield self._model.item(i)

    def allFiltered(self) -> bool:
        return self._proxy.rowCount() == 0

    def isEmpty(self) -> bool:
        return self._model.rowCount() == 0

    def filter(self, text: str):
        self._proxy.setFilterFixedString(text)
        self._adjust_fixed_height()

    def proxy(self) -> EmojiSortFilterProxyModel:
        return self._proxy