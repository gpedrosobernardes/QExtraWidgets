from enum import Enum
from functools import lru_cache
import typing

from PySide6.QtGui import QStandardItem, Qt
from emoji_data_python import EmojiChar, emoji_data, find_by_shortname

from qextrawidgets.gui.items.emoji_category_item import QEmojiCategoryItem


class EmojiSkinTone(str, Enum):
    """Skin tone modifiers (Fitzpatrick scale) supported by Unicode.

    Inherits from 'str' to facilitate direct concatenation with base emojis.

    Attributes:
        Default: Default skin tone (usually yellow/neutral). No modifier.
        Light: Type 1-2: Light skin tone.
        MediumLight: Type 3: Medium-light skin tone.
        Medium: Type 4: Medium skin tone.
        MediumDark: Type 5: Medium-dark skin tone.
        Dark: Type 6: Dark skin tone.
    """

    # Default (Generally Yellow/Neutral) - Adds no code
    Default = ""

    # Type 1-2: Light Skin
    Light = "1F3FB"

    # Type 3: Medium-Light Skin
    MediumLight = "1F3FC"

    # Type 4: Medium Skin
    Medium = "1F3FD"

    # Type 5: Medium-Dark Skin
    MediumDark = "1F3FE"

    # Type 6: Dark Skin
    Dark = "1F3FF"


@lru_cache(maxsize=None)
def _find_emoji_by_char(char: str) -> typing.Optional[EmojiChar]:
    """
    Find an EmojiChar object by its character string.
    Cached for performance.
    """
    return next((e for e in emoji_data if e.char == char), None)


@lru_cache(maxsize=None)
def _find_emoji_by_short_name(short_name: str) -> typing.Optional[EmojiChar]:
    """
    Find an EmojiChar object by one of its short names.
    Cached for performance.
    """
    # Remove colons if present (e.g. :smile: -> smile)
    clean_name = short_name.strip(":")
    matches = find_by_shortname(clean_name)
    for emoji in matches:
        if emoji.short_names and clean_name in emoji.short_names:
            return emoji
    return None


class QEmojiItem(QStandardItem):
    """A standard item representing a single emoji in the model."""

    class QEmojiDataRole(int, Enum):
        """
        Custom data roles for the emoji item.
        """

        SkinToneRole = Qt.ItemDataRole.UserRole + 1
        CategoryRole = Qt.ItemDataRole.UserRole + 2
        EmojiRole = Qt.ItemDataRole.UserRole + 3
        ShortNamesRole = Qt.ItemDataRole.UserRole + 4

    def __init__(self, emoji_char: EmojiChar, skin_tone: str = ""):
        """
        Initializes the emoji item.

        Args:
            emoji_char (EmojiChar): The emoji character data object.
            skin_tone (str, optional): The skin tone modifier (hex code). Defaults to "".
        """
        super().__init__()
        self.setData(emoji_char, Qt.ItemDataRole.UserRole)
        self.setData(skin_tone, self.QEmojiDataRole.SkinToneRole)
        self.setEditable(False)

    @classmethod
    def fromEmoji(cls, emoji: str, skin_tone: str = "") -> "QEmojiItem":
        """
        Create a QEmojiItem from an emoji character string.

        Args:
            emoji (str): The emoji character.
            skin_tone (str, optional): Skin tone modifier.

        Returns:
            QEmojiItem: The created item.

        Raises:
            ValueError: If the emoji is not found in the database.
        """
        emoji_char = _find_emoji_by_char(emoji)
        if not emoji_char:
            raise ValueError(f"Emoji '{emoji}' not found in emoji database.")
        return cls(emoji_char, skin_tone)

    @classmethod
    def fromEmojiShortName(cls, short_name: str, skin_tone: str = "") -> "QEmojiItem":
        """
        Create a QEmojiItem from a short name (e.g., 'smile' or ':smile:').

        Args:
            short_name (str): The short name of the emoji.
            skin_tone (str, optional): Skin tone modifier.

        Returns:
            QEmojiItem: The created item.

        Raises:
            ValueError: If the emoji is not found by short name.
        """
        emoji_char = _find_emoji_by_short_name(short_name)
        if not emoji_char:
            raise ValueError(f"Emoji with short name '{short_name}' not found.")
        return cls(emoji_char, skin_tone)

    def emojiChar(self) -> EmojiChar:
        """
        Returns the raw EmojiChar object associated with this item.

        Returns:
            EmojiChar: The emoji character data object.
        """
        return self.data(Qt.ItemDataRole.UserRole)

    def coloredEmojiChar(self) -> EmojiChar:
        """
        Returns the EmojiChar corresponding to the set skin tone, if available.
        Otherwise, returns the base EmojiChar.

        Returns:
            EmojiChar: The processed emoji character data object.
        """
        emoji_char = self.emojiChar()
        skin_tone = self.skinTone()
        if (
            skin_tone
            and self.skinToneCompatible(emoji_char)
            and skin_tone in emoji_char.skin_variations
        ):
            return emoji_char.skin_variations[skin_tone]
        return emoji_char

    @staticmethod
    def skinToneCompatible(emoji_char: EmojiChar) -> bool:
        """
        Checks if the given emoji supports skin tone variations in the library.

        Args:
            emoji_char (EmojiChar): The emoji to check.

        Returns:
            bool: True if it supports skin tone variations, False otherwise.
        """
        return any(
            skin_tone in emoji_char.skin_variations for skin_tone in EmojiSkinTone
        )

    def emoji(self) -> str:
        """Returns the emoji character.

        Returns:
            str: The emoji character.
        """
        return self.coloredEmojiChar().char

    def shortNames(self) -> typing.List[str]:
        """
        Returns a list of short names (keywords) for the emoji.

        Returns:
            typing.List[str]: List of short names.
        """
        return self.emojiChar().short_names or []

    def aliasesText(self) -> str:
        """
        Returns a string containing all short names formatted as aliases (e.g. :smile: :happy:).

        Returns:
            str: Space-separated aliases.
        """
        return " ".join(f":{a}:" for a in self.shortNames())

    def firstAlias(self) -> str:
        """
        Returns the first alias/short name of the emoji.

        Returns:
            str: The first alias, or None/IndexError if empty (though usually not empty).
        """
        return self.shortNames()[0]

    def skinTone(self) -> str:
        """
        Returns the current skin tone hex string stored in data.

        Returns:
            str: The skin tone hex string (e.g., '1F3FB') or empty string.
        """
        return self.data(self.QEmojiDataRole.SkinToneRole)

    def clone(self, /):
        """
        Creates a copy of this QEmojiItem.

        Returns:
            QEmojiItem: A new instance with the same emoji and skin tone.
        """
        return QEmojiItem(self.emojiChar(), self.skinTone())

    def data(self, role: int = Qt.ItemDataRole.UserRole) -> typing.Any:
        """
        Retrieves data for the given role.

        Args:
            role (int): The data role.

        Returns:
            typing.Any: The data associated with the role.
        """
        if role == self.QEmojiDataRole.CategoryRole:
            return self.emojiChar().category

        if role == self.QEmojiDataRole.EmojiRole:
            return self.emojiChar().char

        if role == self.QEmojiDataRole.ShortNamesRole:
            return self.shortNames()

        return super().data(role)

    def parent(self) -> typing.Optional[QEmojiCategoryItem]:  # type: ignore[override]
        """
        Returns the parent item of the emoji item.

        Returns:
            QEmojiCategoryItem: The parent category item.
        """
        item = super().parent()
        if isinstance(item, QEmojiCategoryItem):
            return item
        return None
