import typing

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QListView, QTreeView, QSizePolicy, QAbstractScrollArea
from emojis.db import Emoji

from extra_qwidgets.abc_widgets.emoji_picker.emoji_sort_filter_proxy_model import EmojiSortFilterProxyModel


class QEmojiGrid(QListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = QStandardItemModel()
        # self.proxy = EmojiSortFilterProxyModel(self)
        # self.proxy.setSourceModel(self.model)
        self.setModel(self.model)
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

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._adjust_fixed_height()

    def _adjust_fixed_height(self):
        itens_total = self.model.rowCount()
        if itens_total == 0:
            return
        item_size = self.gridSize()
        width = self.size().width()
        if item_size.width() == 0:
            return
        items_per_row = max(1, width // item_size.width())
        rows = -(-itens_total // items_per_row)
        total_height = rows * item_size.height()
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
            if item.data() == emoji:
                return item
        return None

    def allHidden(self) -> bool:
        return self.proxy.rowCount() == 0

    def isEmpty(self) -> bool:
        return self.model.rowCount() == 0

    def filter(self, text: str):
        self.proxy.setFilterFixedString(text)
        self.updateGeometry()