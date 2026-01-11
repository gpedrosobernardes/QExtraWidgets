import typing
from enum import IntEnum

from PySide6.QtCore import QSize
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt


class QEmojiDataRole(IntEnum):
    AliasRole = Qt.ItemDataRole.UserRole + 1
    CategoryRole = Qt.ItemDataRole.UserRole + 2
    RecentRole = Qt.ItemDataRole.UserRole + 3
    FavoriteRole = Qt.ItemDataRole.UserRole + 4
    SkinTonesRole =  Qt.ItemDataRole.UserRole + 5
    YellowEmojiRole = Qt.ItemDataRole.UserRole + 6


class QEmojiModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self._emoji_size_hint = None

    def setEmojiSize(self, size: QSize):
        self._emoji_size_hint = size

        for row in range(self.rowCount()):
            item = self.item(row)
            item.setSizeHint(self.emojiSize())


    def emojiSize(self) -> QSize:
        return self._emoji_size_hint

    def addEmoji(self, emoji: str, alias: str, category: str, recent: bool = False, favorite: bool = False, skin_tones: typing.List[str] = None):
        item = QStandardItem(emoji)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        item.setData(alias, QEmojiDataRole.AliasRole)
        item.setData(category, QEmojiDataRole.CategoryRole)
        item.setData(recent, QEmojiDataRole.RecentRole)
        item.setData(favorite, QEmojiDataRole.FavoriteRole)
        item.setData(skin_tones, QEmojiDataRole.SkinTonesRole)
        item.setData(emoji, QEmojiDataRole.YellowEmojiRole)
        self.appendRow(item)

    def emojiItem(self, emoji: str) -> typing.Optional[QStandardItem]:
        items = self.findItems(emoji, Qt.MatchFlag.MatchExactly, column=0)
        if items:
            return items[0]
        return None

    def removeEmoji(self, emoji: str):
        self.removeRow(self.emojiItem(emoji).row())

    def setFavoriteEmoji(self, emoji: str, favorite: bool):
        item = self.emojiItem(emoji)
        if item:
            item.setData(favorite, QEmojiDataRole.FavoriteRole)

    def setRecentEmoji(self, emoji: str, recent: bool):
        item = self.emojiItem(emoji)
        if item:
            item.setData(recent, QEmojiDataRole.RecentRole)