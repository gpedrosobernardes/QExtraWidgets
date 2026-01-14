import typing
from enum import IntEnum, StrEnum

from PySide6.QtCore import QSize
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt, QIcon


class QEmojiDataRole(IntEnum):
    AliasRole = Qt.ItemDataRole.UserRole + 1
    CategoryRole = Qt.ItemDataRole.UserRole + 2
    RecentRole = Qt.ItemDataRole.UserRole + 3
    FavoriteRole = Qt.ItemDataRole.UserRole + 4
    SkinTonesRole =  Qt.ItemDataRole.UserRole + 5
    HasSkinTonesRole = Qt.ItemDataRole.UserRole + 6


class EmojiSkinTone(StrEnum):
    """
    Modificadores de tom de pele (Fitzpatrick scale) suportados pelo Windows/Unicode.
    Herda de 'str' para facilitar a concatenação direta.
    """

    # Padrão (Geralmente Amarelo/Neutro) - Não adiciona nenhum código
    Default = ""

    # Tipo 1-2: Pele Clara
    Light = "1F3FB"  # 🏻

    # Tipo 3: Pele Morena Clara
    MediumLight = "1F3FC"  # 🏼

    # Tipo 4: Pele Morena
    Medium = "1F3FD"  # 🏽

    # Tipo 5: Pele Morena Escura
    MediumDark = "1F3FE"  # 🏾

    # Tipo 6: Pele Escura
    Dark = "1F3FF"  # 🏿


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
        item.setData(emoji, Qt.ItemDataRole.UserRole)
        item.setData(alias, QEmojiDataRole.AliasRole)
        item.setData(category, QEmojiDataRole.CategoryRole)
        item.setData(recent, QEmojiDataRole.RecentRole)
        item.setData(favorite, QEmojiDataRole.FavoriteRole)
        item.setData(skin_tones, QEmojiDataRole.SkinTonesRole)
        item.setData(bool(skin_tones), QEmojiDataRole.HasSkinTonesRole)
        self.appendRow(item)

    def setSkinTone(self, skin_tone: str):
        for row in range(self.rowCount()):
            item = self.item(row)
            skin_tones: dict = item.data(QEmojiDataRole.SkinTonesRole)
            if skin_tones:
                item.setData(skin_tones[skin_tone], Qt.ItemDataRole.UserRole)

    def emojiItem(self, emoji: str) -> typing.Optional[QStandardItem]:
        items = self.findItems(emoji, Qt.MatchFlag.MatchExactly, column=0)
        if items:
            return items[0]
        return None

    def filterEmojisItems(self, role: typing.Union[QEmojiDataRole, Qt.ItemDataRole], value) -> typing.List[QStandardItem]:
        return [self.itemFromIndex(index) for index in self.match(self.index(0, 0), role, value, -1, Qt.MatchFlag.MatchExactly)]

    def getEmojiItems(self) -> typing.List[QStandardItem]:
        return [self.item(row) for row in range(self.rowCount())]

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

    def clearEmojis(self):
        for row in range(self.rowCount()):
            item = self.item(row)
            item.setIcon(QIcon())
            item.setText("")