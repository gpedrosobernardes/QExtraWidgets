from enum import Enum

from PySide6.QtGui import QStandardItem, Qt
from emoji_data_python import EmojiChar
import typing


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


class QEmojiItem(QStandardItem):
    """A standard item representing a single emoji in the model."""

    class QEmojiDataRole(int, Enum):
        SkinToneRole = Qt.ItemDataRole.UserRole + 1
        CategoryRole = Qt.ItemDataRole.UserRole + 2
        EmojiRole = Qt.ItemDataRole.UserRole + 3
        ShortNamesRole = Qt.ItemDataRole.UserRole + 4

    def __init__(self, emoji_char: EmojiChar, skin_tone: str = ""):
        super().__init__()
        self.setData(emoji_char, Qt.ItemDataRole.UserRole)
        self.setData(skin_tone, self.QEmojiDataRole.SkinToneRole)
        self.setEditable(False)

    def emojiChar(self) -> EmojiChar:
        return self.data(Qt.ItemDataRole.UserRole)

    def coloredEmojiChar(self) -> EmojiChar:
        emoji_char = self.emojiChar()
        skin_tone = self.skinTone()
        if skin_tone and self.skinToneCompatible(emoji_char) and skin_tone in emoji_char.skin_variations:
            return emoji_char.skin_variations[skin_tone]
        return emoji_char

    @staticmethod
    def skinToneCompatible(emoji_char: EmojiChar) -> bool:
        return any(skin_tone in emoji_char.skin_variations for skin_tone in EmojiSkinTone)

    def emoji(self) -> str:
        """Returns the emoji character.

        Returns:
            str: The emoji character.
        """
        return self.coloredEmojiChar().char

    def shortNames(self) -> typing.List[str]:
        return self.emojiChar().short_names or []

    def aliasesText(self) -> str:
        return " ".join(f":{a}:" for a in self.shortNames())

    def firstAlias(self) -> str:
        return self.shortNames()[0]

    def skinTone(self) -> str:
        return self.data(self.QEmojiDataRole.SkinToneRole)

    def clone(self, /):
        return QEmojiItem(self.emojiChar(), self.skinTone())

    def data(self, role: int = Qt.ItemDataRole.UserRole) -> typing.Any:
        if role == self.QEmojiDataRole.CategoryRole:
            return self.emojiChar().category

        if role == self.QEmojiDataRole.EmojiRole:
            return self.emojiChar().char

        if role == self.QEmojiDataRole.ShortNamesRole:
            return self.shortNames()

        return super().data(role)