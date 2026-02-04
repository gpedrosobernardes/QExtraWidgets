from enum import Enum

from PySide6.QtCore import QT_TRANSLATE_NOOP, Signal, QModelIndex, Slot
from PySide6.QtGui import QStandardItemModel, Qt
from emoji_data_python import emoji_data
import typing

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
    """
    Model for managing emoji categories and items using QStandardItemModel.

    This model organizes emojis into categories (e.g., Smileys & Emotion, Animals & Nature)
    and supports optional 'Favorites' and 'Recents' categories. It also handles skin tone
    updates for compatible emojis.

    Attributes:
        categoryInserted (Signal(QEmojiCategoryItem)): Emitted when a category is added.
        categoryRemoved (Signal(QEmojiCategoryItem)): Emitted when a category is removed.
        skinToneChanged (Signal(QModelIndex)): Emitted when a skin tone is applied to an emoji.
    """
    categoryInserted = Signal(QEmojiCategoryItem)
    categoryRemoved = Signal(QEmojiCategoryItem)
    skinToneChanged = Signal(QModelIndex)
    _emojis_skin_modifier_compatible = {}

    def __init__(self, favorite_category: bool = True, recent_category: bool = True):
        """
        Initialize the QEmojiPickerModel.

        Args:
            favorite_category (bool): Whether to include the Favorites category. Defaults to True.
            recent_category (bool): Whether to include the Recents category. Defaults to True.
        """
        super().__init__()
        self._favorite_category = favorite_category
        self._recent_category = recent_category

        self.rowsInserted.connect(self._on_rows_inserted)
        self.rowsAboutToBeRemoved.connect(self._on_rows_removed)

    def populate(self):
        """
        Populate the model with emoji categories and items.

        Iterates through the emoji database, groups emojis by category, and creates the hierarchical model structure.
        Compatible emojis are tracked for skin tone updates.
        """
        self._emojis_skin_modifier_compatible.clear()

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
                item = QEmojiItem(emoji_char)
                if emoji_char.category not in emoji_grouped_by_category:
                    emoji_grouped_by_category[emoji_char.category] = []
                emoji_grouped_by_category[emoji_char.category].append(item)
                support_skin_modifiers = QEmojiItem.skinToneCompatible(emoji_char)
                if support_skin_modifiers:
                    if emoji_char.category not in self._emojis_skin_modifier_compatible:
                        self._emojis_skin_modifier_compatible[emoji_char.category] = []
                    self._emojis_skin_modifier_compatible[emoji_char.category].append(emoji_char.char)

        if self._recent_category:
            icon = QThemeResponsiveIcon.fromAwesome(icons[EmojiCategory.Recents])
            recent_category_item = QEmojiCategoryItem(EmojiCategory.Recents, icon)
            self.appendRow(recent_category_item)

        if self._favorite_category:
            icon = QThemeResponsiveIcon.fromAwesome(icons[EmojiCategory.Favorites])
            favorite_category_item = QEmojiCategoryItem(EmojiCategory.Favorites, icon)
            self.appendRow(favorite_category_item)

        for category, emoji_items in emoji_grouped_by_category.items():
            icon = QThemeResponsiveIcon.fromAwesome(icons[category])
            category_item = QEmojiCategoryItem(category, icon)
            self.appendRow(category_item)
            category_item.appendRows(emoji_items)



    def findEmojiInCategory(self, category_index: QModelIndex, emoji: str) -> typing.Optional[QModelIndex]:
        """
        Find a specific emoji within a given category index.

        Args:
            category_index (QModelIndex): The index of the category to search in.
            emoji (str): The emoji character to find.

        Returns:
            Optional[QModelIndex]: The index of the found emoji, or None if not found.
        """
        # match(start_index, role, value, hits, flags)
        # Search starting from the first child of the category
        start_index = self.index(0, 0, category_index)

        # We only want direct children, so we don't use Qt.MatchChange.MatchRecursive.
        matches = self.match(
            start_index,
            QEmojiItem.QEmojiDataRole.EmojiRole,
            emoji,
            1,  # Number of results (1 to stop at the first)
            Qt.MatchFlag.MatchExactly
        )

        if matches:
            return matches[0]
        return None

    def findCategory(self, category_name: str) -> typing.Optional[QModelIndex]:
        """
        Find a category by its name.

        Args:
            category_name (str): The name of the category to search for.

        Returns:
            Optional[QModelIndex]: The index of the category, or None if not found.
        """
        start_index = self.index(0, 0)
        matches = self.match(
            start_index,
            QEmojiCategoryItem.QEmojiCategoryDataRole.CategoryRole,
            category_name,
            1,
            Qt.MatchFlag.MatchExactly
        )
        if matches:
            return matches[0]
        return None

    def setSkinTone(self, skin_tone: str):
        """
        Update the skin tone for all compatible emojis in the model.

        Iterates through tracked compatible emojis and updates their data with the new skin tone.

        Args:
            skin_tone (str): The new skin tone character/code.
        """
        for category, emojis_with_skin_modifier in self._emojis_skin_modifier_compatible.items():
            category_index = self.findCategory(category)
            if not category_index:
                return

            for emoji in emojis_with_skin_modifier:
                emoji_index = self.findEmojiInCategory(category_index, emoji)
                if not emoji_index:
                    continue

                emoji_item = self.itemFromIndex(emoji_index)
                emoji_item.setData(skin_tone, QEmojiItem.QEmojiDataRole.SkinToneRole)
                self.skinToneChanged.emit(emoji_index)

    @Slot(QModelIndex, int, int)
    def _on_rows_removed(self, parent: QModelIndex, first: int, last: int):
        """
        Handle internal slot for rows removed signal.

        Emits categoryRemoved signal when top-level rows (categories) are removed.

        Args:
            parent (QModelIndex): The parent index.
            first (int): The first removed row.
            last (int): The last removed row.
        """
        if parent.isValid():
            return

        for row in range(first, last + 1):
            item = self.item(row)
            if isinstance(item, QEmojiCategoryItem):
                self.categoryRemoved.emit(item)

    @Slot(QModelIndex, int, int)
    def _on_rows_inserted(self, parent: QModelIndex, first: int, last: int):
        """
        Handle internal slot for rows inserted signal.

        Emits categoryInserted signal when top-level rows (categories) are added.

        Args:
            parent (QModelIndex): The parent index.
            first (int): The first inserted row.
            last (int): The last inserted row.
        """
        if parent.isValid():
            return

        for row in range(first, last + 1):
            item = self.item(row)
            if isinstance(item, QEmojiCategoryItem):
                self.categoryInserted.emit(item)

