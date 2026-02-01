from enum import Enum

from PySide6.QtCore import QT_TRANSLATE_NOOP, Signal
from PySide6.QtGui import QStandardItemModel, QIcon
from emoji_data_python import emoji_data

from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.items.emoji_category_item import QEmojiCategoryItem
from qextrawidgets.items.emoji_item import QEmojiItem


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


class QEmojiPickerModel(QStandardItemModel):
    categoryInserted = Signal(QEmojiCategoryItem)

    def __init__(self, favorite_category: bool = False, recent_category: bool = False):
        super().__init__()
        self._favorite_category = favorite_category
        self._recent_category = recent_category

    def populate(self):
        icons = {
            EmojiCategory.Activities: "fa6s.gamepad",
            EmojiCategory.FoodAndDrink: "fa6s.bowl-food",
            EmojiCategory.AnimalsAndNature: "fa6s.leaf",
            EmojiCategory.PeopleAndBody: "fa6s.user",
            EmojiCategory.Symbols: "fa6s.heart",
            EmojiCategory.Flags: "fa6s.flag",
            EmojiCategory.TravelAndPlaces: "fa6s.bicycle",
            EmojiCategory.Objects: "fa6s.lightbulb",
            EmojiCategory.SmileysAndEmotion: "fa6s.face-smile",
            EmojiCategory.Favorites: "fa6s.star",
            EmojiCategory.Recents: "fa6s.clock-rotate-left"
        }

        emoji_grouped_by_category = {}

        for emoji_char in sorted(emoji_data, key=lambda e: e.sort_order):
            if emoji_char.category != "Component":
                item = QEmojiItem(emoji_char.char, emoji_char.short_names)
                if emoji_char.category not in emoji_grouped_by_category:
                    emoji_grouped_by_category[emoji_char.category] = []
                emoji_grouped_by_category[emoji_char.category].append(item)

        for category, emoji_items in emoji_grouped_by_category.items():
            icon = QThemeResponsiveIcon.fromAwesome(icons[category])
            category_item = QEmojiCategoryItem(category, icon)
            self.appendRow(category_item)
            category_item.appendRows(emoji_items)
            self.categoryInserted.emit(category_item)