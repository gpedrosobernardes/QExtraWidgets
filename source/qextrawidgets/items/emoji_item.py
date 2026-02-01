import typing
from enum import Enum

from PySide6.QtGui import QStandardItem, Qt
from emoji_data_python import EmojiChar


class QEmojiItem(QStandardItem):
    """A standard item representing a single emoji in the model."""

    def __init__(self, emoji: str, alias: typing.List[str], category: typing.Optional[str] = None):
        """Initializes the emoji item.

        Args:
            emoji (str): The emoji character.
            alias (str): The text alias (e.g., ":smile:").
            category (str): The category the emoji belongs to.
        """
        super().__init__(emoji)
        self.setData(emoji, Qt.ItemDataRole.EditRole)
        self.setData(alias, QEmojiDataRole.AliasRole)
        if category:
            self.setData(category, QEmojiDataRole.CategoryRole)
        self.setEditable(False)

    def emoji(self) -> str:
        """Returns the emoji character.

        Returns:
            str: The emoji character.
        """
        return self.data(Qt.ItemDataRole.EditRole)

    def rawAlias(self) -> typing.List[str]:
        """Returns the text alias.

        Returns:
            str: The text alias.
        """
        return self.data(QEmojiDataRole.AliasRole)

    def aliasesText(self) -> str:
        return " ".join(f":{a}:" for a in self.rawAlias())

    def firstAlias(self) -> str:
        return self.rawAlias()[0]

    def category(self) -> typing.Optional[str]:
        """Returns the category.

        Returns:
            str: The category.
        """
        return self.data(QEmojiDataRole.CategoryRole)

    def clone(self, /):
        return QEmojiItem(self.emoji(), self.rawAlias(), self.category())


class QEmojiDataRole(int, Enum):
    """Custom item data roles for emoji-related data in models.

    Attributes:
        AliasRole: Role for emoji text aliases (e.g., ":smile:").
        CategoryRole: Role for emoji category names.
    """
    AliasRole = Qt.ItemDataRole.UserRole + 1
    CategoryRole = Qt.ItemDataRole.UserRole + 2
