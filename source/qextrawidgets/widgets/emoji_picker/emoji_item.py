import typing

from PySide6.QtGui import QStandardItem, Qt

from qextrawidgets.widgets.emoji_picker.enums import EmojiSkinTone, QEmojiDataRole


class QEmojiItem(QStandardItem):
    """A standard item representing a single emoji in the model."""

    def __init__(self, emoji: str, alias: str, category: str, recent: bool = False, favorite: bool = False,
                 skin_tones: typing.Dict[EmojiSkinTone, str] = None):
        """Initializes the emoji item.

        Args:
            emoji (str): The emoji character.
            alias (str): The text alias (e.g., ":smile:").
            category (str): The category the emoji belongs to.
            recent (bool, optional): Whether the emoji is in the recent list. Defaults to False.
            favorite (bool, optional): Whether the emoji is a favorite. Defaults to False.
            skin_tones (Dict[EmojiSkinTone, str], optional): Dictionary mapping skin tones to emoji variations. Defaults to None.
        """
        super().__init__(emoji)
        self.setData(emoji, Qt.ItemDataRole.EditRole)
        self.setData(alias, QEmojiDataRole.AliasRole)
        self.setData(category, QEmojiDataRole.CategoryRole)
        self.setData(recent, QEmojiDataRole.RecentRole)
        self.setData(favorite, QEmojiDataRole.FavoriteRole)
        self.setData(skin_tones, QEmojiDataRole.SkinTonesRole)
        self.setData(bool(skin_tones), QEmojiDataRole.HasSkinTonesRole)

    def emoji(self) -> str:
        """Returns the emoji character.

        Returns:
            str: The emoji character.
        """
        return self.data(Qt.ItemDataRole.EditRole)

    def alias(self) -> str:
        """Returns the text alias.

        Returns:
            str: The text alias.
        """
        return self.data(QEmojiDataRole.AliasRole)