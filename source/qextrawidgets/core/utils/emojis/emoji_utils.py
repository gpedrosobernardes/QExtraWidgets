"""
Utilities for working with emojis and skin tone modifiers in Qt applications.

This module provides:
- `EmojiSkinTone`: Enum representing the six Fitzpatrick skin tone scale modifiers.
- `QEmojiUtils`: Static utility class for querying, filtering, and combining emojis
  with skin tone variants using the `emoji_data_python` library.
"""

import logging
import typing
from enum import Enum
from functools import lru_cache

from PySide6.QtCore import Qt
from emoji_data_python import EmojiChar, emoji_data

from qextrawidgets.gui.items import QIconItem


class EmojiSkinTone(str, Enum):
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

    Default     = ""        # No modifier appended
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

    @staticmethod
    def combineEmojiWithSkinTone(
        emoji: typing.Union[EmojiChar, str],
        skin_tone: str,
        fallback_on_default: bool = True,
    ) -> typing.Optional[EmojiChar]:
        """Return the skin-toned variant of an emoji, with optional fallback.

        Looks up the requested ``skin_tone`` modifier inside the emoji's
        ``skin_variations`` dictionary. When the variant is unavailable, the
        behavior is controlled by ``fallback_on_default``.

        Args:
            emoji: The base emoji, either as an ``EmojiChar`` instance or as a
                raw Unicode string (e.g. ``"👋"``). If a string is provided,
                it is resolved via :meth:`findEmojiByChar` first.
            skin_tone: The skin tone code point string to apply
                (e.g. ``EmojiSkinTone.Dark`` → ``"1F3FF"``). Pass an empty
                string or ``EmojiSkinTone.Default`` to skip tone application
                and return the base emoji directly.
            fallback_on_default: When ``True`` (default) and the requested skin
                tone variant is not available, the base emoji is returned as a
                fallback. When ``False``, ``None`` is returned instead.

        Returns:
            - The ``EmojiChar`` for the requested skin tone variant if found.
            - The base ``EmojiChar`` if the variant is missing and
              ``fallback_on_default`` is ``True``.
            - ``None`` if the base emoji cannot be resolved, or if the variant
              is missing and ``fallback_on_default`` is ``False``.

        Example::

            waving = "👋"
            result = QEmojiUtils.combineEmojiWithSkinTone(waving, EmojiSkinTone.Dark)
            if result:
                print(result.char)  # "👋🏿"
        """
        if isinstance(emoji, EmojiChar):
            emoji_char = emoji
        else:
            emoji_char = QEmojiUtils.findEmojiByChar(emoji)
            if emoji_char is None:
                return None

        if skin_tone:
            emoji_with_skin_tone = emoji_char.skin_variations.get(skin_tone)
            if emoji_with_skin_tone is None:
                logging.debug(f"Skin tone {skin_tone} not found for emoji {emoji}")
            else:
                return emoji_with_skin_tone

        if fallback_on_default:
            return emoji_char

        return None

    @staticmethod
    @lru_cache(maxsize=None)
    def findEmojiByChar(char: str) -> typing.Optional[EmojiChar]:
        """Resolve a Unicode emoji string to its ``EmojiChar`` data object.

        Performs a linear search over the global ``emoji_data`` list and returns
        the first entry whose ``.char`` attribute matches ``char`` exactly.
        Results are cached indefinitely via ``lru_cache`` so repeated lookups
        for the same character are O(1) after the first call.

        Args:
            char: A Unicode emoji string to look up (e.g. ``"😀"``).

        Returns:
            The matching ``EmojiChar`` instance, or ``None`` if no entry in
            ``emoji_data`` matches the given character.

        Note:
            Because this method is decorated with ``@lru_cache``, its argument
            must be hashable. Plain strings satisfy this requirement.
        """
        return next((e for e in emoji_data if e.char == char), None)

    @staticmethod
    def supportSkinTones(char: EmojiChar) -> bool:
        """Check whether an emoji exposes all six Fitzpatrick skin tone variants.

        An emoji is considered to *fully* support skin tones only when every
        non-default ``EmojiSkinTone`` value is present as a key in its
        ``skin_variations`` dictionary. Partial support (i.e. only some
        modifiers available) is treated as unsupported.

        Args:
            char: The ``EmojiChar`` instance to inspect.

        Returns:
            ``True`` if ``char.skin_variations`` is non-empty **and** contains
            entries for all five non-default skin tone codes; ``False`` otherwise.

        Example::

            thumbs_up = QEmojiUtils.findEmojiByChar("👍")
            QEmojiUtils.supportSkinTones(thumbs_up)  # True

            globe = QEmojiUtils.findEmojiByChar("🌍")
            QEmojiUtils.supportSkinTones(globe)       # False
        """
        if char.skin_variations:
            return all(
                skin_tone.value in char.skin_variations
                for skin_tone in EmojiSkinTone
                if skin_tone != EmojiSkinTone.Default
            )

        return False

    @staticmethod
    def emojisWithSkinTones() -> typing.List[EmojiChar]:
        """Return every emoji in the dataset that fully supports skin tone variants.

        Filters the global ``emoji_data`` list using :meth:`supportSkinTones`,
        keeping only emojis for which all five Fitzpatrick modifier variants are
        defined.

        Returns:
            A new list of ``EmojiChar`` objects that support all skin tones.
            The order mirrors the original ``emoji_data`` ordering. The list may
            be empty if the dataset contains no such emojis.

        Example::

            skinnable = QEmojiUtils.emojisWithSkinTones()
            print(len(skinnable))          # e.g. 130
            print(skinnable[0].char)       # e.g. "👋"
        """
        return list(filter(QEmojiUtils.supportSkinTones, emoji_data))

    @staticmethod
    def getEmojiWithSkinToneByIconItem(icon_item: QIconItem, fallback_to_default: bool = True) -> typing.Optional[EmojiChar]:
        emoji = icon_item.data(Qt.ItemDataRole.EditRole)
        skin_tone = icon_item.data(QIconItem.QIconItemDataRole.ColorModifierRole)
        return QEmojiUtils.combineEmojiWithSkinTone(emoji, skin_tone, fallback_to_default)