from enum import Enum

from PySide6.QtCore import QT_TRANSLATE_NOOP
from PySide6.QtGui import Qt


class QEmojiDataRole(int, Enum):
    """Custom item data roles for emoji-related data in models.

    Attributes:
        AliasRole: Role for emoji text aliases (e.g., ":smile:").
        CategoryRole: Role for emoji category names.
        RecentRole: Role for boolean indicating if the emoji is recently used.
        FavoriteRole: Role for boolean indicating if the emoji is a favorite.
        SkinTonesRole: Role for dictionary of skin tone variations.
        HasSkinTonesRole: Role for boolean indicating if the emoji supports skin tones.
    """
    AliasRole = Qt.ItemDataRole.UserRole + 1
    CategoryRole = Qt.ItemDataRole.UserRole + 2
    RecentRole = Qt.ItemDataRole.UserRole + 3
    FavoriteRole = Qt.ItemDataRole.UserRole + 4
    SkinTonesRole = Qt.ItemDataRole.UserRole + 5
    HasSkinTonesRole = Qt.ItemDataRole.UserRole + 6


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
    Light = "1F3FB"  # 🏻

    # Type 3: Medium-Light Skin
    MediumLight = "1F3FC"  # 🏼

    # Type 4: Medium Skin
    Medium = "1F3FD"  # 🏽

    # Type 5: Medium-Dark Skin
    MediumDark = "1F3FE"  # 🏾

    # Type 6: Dark Skin
    Dark = "1F3FF"  # 🏿


class EmojiCategory(str, Enum):
    """Standard emoji categories."""
    Activities = QT_TRANSLATE_NOOP("EmojiCategory", "Activities")
    FoodAndDrink = QT_TRANSLATE_NOOP("EmojiCategory", "Food & Drink")
    AnimalsAndNature = QT_TRANSLATE_NOOP("EmojiCategory", "Animals & Nature")
    PeopleAndBody = QT_TRANSLATE_NOOP("EmojiCategory", "People & Body")
    Symbols = QT_TRANSLATE_NOOP("EmojiCategory", "Symbols")
    Flags = QT_TRANSLATE_NOOP("EmojiCategory", "Flags")
    TravelAndPlaces = QT_TRANSLATE_NOOP("EmojiCategory", "Travel & Places")
    Objects = QT_TRANSLATE_NOOP("EmojiCategory", "Objects")
    SmileysAndEmotion = QT_TRANSLATE_NOOP("EmojiCategory", "Smileys & Emotion")
    Favorites = QT_TRANSLATE_NOOP("EmojiCategory", "Favorites")
    Recents = QT_TRANSLATE_NOOP("EmojiCategory", "Recents")
