"""
Utilities for working with emojis and skin tone modifiers in Qt applications.

This module provides:
- `EmojiSkinTone`: Enum representing the six Fitzpatrick skin tone scale modifiers.
- `QEmojiUtils`: Static utility class for querying, filtering, and combining emojis
  with skin tone variants using the `emoji_data_python` library.
"""

import typing
from collections import defaultdict
from enum import Enum

from PySide6.QtGui import QStandardItem, Qt
from emoji_data_python import EmojiChar, emoji_data


class EmojiSkinVariations(str, Enum):
    """Skin tone modifiers based on the Fitzpatrick scale, as defined by Unicode.

    Each value is the Unicode code point (without the U+ prefix) of the
    corresponding modifier character. Inherits from ``str`` to allow direct
    string concatenation with base emoji characters.

    Example::

        base = "👋"
        modifier = EmojiSkinTone.Dark   # "1F3FF"
        # Combine: base + chr(int(modifier, 16))  →  "👋🏿"

    Attributes:
        Default:     Neutral / yellow tone. Carries an empty string — no modifier
                     is appended when this value is used.
        Light:       Fitzpatrick Type 1–2 — very light skin.
        MediumLight: Fitzpatrick Type 3  — light-to-medium skin.
        Medium:      Fitzpatrick Type 4  — medium / olive skin.
        MediumDark:  Fitzpatrick Type 5  — medium-dark skin.
        Dark:        Fitzpatrick Type 6  — dark skin.

    References:
        - Unicode standard: https://unicode.org/reports/tr51/#Diversity
        - Fitzpatrick scale: https://en.wikipedia.org/wiki/Fitzpatrick_scale
    """
    Light       = "1F3FB"   # 🏻  Type 1–2
    MediumLight = "1F3FC"   # 🏼  Type 3
    Medium      = "1F3FD"   # 🏽  Type 4
    MediumDark  = "1F3FE"   # 🏾  Type 5
    Dark        = "1F3FF"   # 🏿  Type 6


class QEmojiUtils:
    """Static utility class for emoji lookup and skin tone manipulation.

    All methods are stateless and exposed as ``@staticmethod``. No instantiation
    is required or intended.

    Responsibilities:
        - Resolve emoji characters to their ``EmojiChar`` data objects.
        - Combine a base emoji with a Fitzpatrick skin tone variant.
        - Introspect whether a given emoji supports skin tone modifications.
        - Filter the global emoji dataset to those that support skin tones.

    Dependencies:
        Relies on the ``emoji_data_python`` library, which exposes ``emoji_data``
        as a flat list of ``EmojiChar`` objects at import time.
    """

    charToEmojiChar = {emoji.char: emoji for emoji in emoji_data}
    skinVariedCharToBaseEmojiChar = {skin_variation.char: emoji for emoji in emoji_data for skin_variation in emoji.skin_variations.values()}
    emojiCharPerCategory = defaultdict(list)

    for emoji in emoji_data:
        emojiCharPerCategory[emoji.category].append(emoji)

    @classmethod
    def applySkinVariation(cls, emoji_char: EmojiChar, skin_variation: typing.Optional[EmojiSkinVariations]) -> EmojiChar:
        try:
            base_emoji_char = cls.getBaseEmoji(emoji_char.char)
        except KeyError:
            base_emoji_char = emoji_char

        if skin_variation is None:
            return base_emoji_char
        else:
            try:
                emoji_with_skin_tone = base_emoji_char.skin_variations[skin_variation]
            except KeyError:
                return base_emoji_char
            else:
                return emoji_with_skin_tone

    @classmethod
    def isSkinVaried(cls, skin_varied_char: str) -> bool:
        try:
            cls.getBaseEmoji(skin_varied_char)
        except KeyError:
            return False
        else:
            return True

    @classmethod
    def findEmojiChar(cls, char: str) -> EmojiChar:
        return cls.charToEmojiChar[char]

    @staticmethod
    def hasSkinVariations(emoji_char: EmojiChar) -> bool:
        return bool(emoji_char.skin_variations)

    @staticmethod
    def skinVariedEmojis() -> typing.Iterator[EmojiChar]:
        return filter(QEmojiUtils.hasSkinVariations, emoji_data)

    @classmethod
    def getBaseEmoji(cls, skin_varied_char: str):
        return cls.skinVariedCharToBaseEmojiChar[skin_varied_char]

    @classmethod
    def getEmojiCharsByCategory(cls, category: str) -> typing.List[EmojiChar]:
        return cls.emojiCharPerCategory[category]