import typing
from enum import Enum

from PySide6.QtGui import QStandardItem, Qt
from emoji_data_python import EmojiChar

from qextrawidgets.gui.items import QIconCategoryItem


class QIconItem(QStandardItem):
    """A standard item representing an icon in the model."""

    class QIconItemDataRole(int, Enum):
        """
        Custom data roles for the icon item.
        """
        SupportColorModifier = Qt.ItemDataRole.UserRole + 1
        ColorModifierRole = Qt.ItemDataRole.UserRole + 2

    def __init__(self, text: str, support_color_modifier: bool, aliases: typing.Optional[typing.List[str]] = None, color_modifier: typing.Optional[str] = None):
        super().__init__()
        self.setData(text, Qt.ItemDataRole.EditRole)
        self.setData(support_color_modifier, QIconItem.QIconItemDataRole.SupportColorModifier)
        if aliases:
            self.setData(aliases, Qt.ItemDataRole.UserRole)
        if color_modifier:
            self.setData(color_modifier, QIconItem.QIconItemDataRole.ColorModifierRole)

    def parent(self) -> typing.Optional[QIconCategoryItem]:  # type: ignore[override]
        """
        Returns the parent item of the emoji item.

        Returns:
            QIconCategoryItem: The parent category item.
        """
        item = super().parent()
        if isinstance(item, QIconCategoryItem):
            return item
        return None

    def clone(self, /):
        """
        Creates a copy of this QIconItem.

        Returns:
            QIconItem: A copy of this QIconItem.
        """
        return QIconItem(self.data(Qt.ItemDataRole.EditRole),
                         self.data(QIconItem.QIconItemDataRole.SupportColorModifier),
                         self.data(Qt.ItemDataRole.UserRole),
                         self.data(QIconItem.QIconItemDataRole.ColorModifierRole))

    @staticmethod
    def fromEmojiChar(emoji_char: EmojiChar):
        return QIconItem(emoji_char.char, bool(emoji_char.skin_variations), emoji_char.short_names)
