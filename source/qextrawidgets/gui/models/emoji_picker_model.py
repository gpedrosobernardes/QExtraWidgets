from enum import Enum

from PySide6.QtCore import QT_TRANSLATE_NOOP, Signal, QModelIndex, Slot
from PySide6.QtGui import QStandardItemModel, Qt, QIcon, QPixmap
from emoji_data_python import emoji_data, EmojiChar
import typing

from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.gui.items.emoji_category_item import QEmojiCategoryItem
from qextrawidgets.gui.items.emoji_item import QEmojiItem


class EmojiCategory(str, Enum):
    """Standard emoji categories."""

    Recents = QT_TRANSLATE_NOOP("EmojiCategory", "Recents")
    Favorites = QT_TRANSLATE_NOOP("EmojiCategory", "Favorites")
    SmileysAndEmotion = QT_TRANSLATE_NOOP("EmojiCategory", "Smileys & Emotion")
    PeopleAndBody = QT_TRANSLATE_NOOP("EmojiCategory", "People & Body")
    AnimalsAndNature = QT_TRANSLATE_NOOP("EmojiCategory", "Animals & Nature")
    FoodAndDrink = QT_TRANSLATE_NOOP("EmojiCategory", "Food & Drink")
    Symbols = QT_TRANSLATE_NOOP("EmojiCategory", "Symbols")
    Activities = QT_TRANSLATE_NOOP("EmojiCategory", "Activities")
    Objects = QT_TRANSLATE_NOOP("EmojiCategory", "Objects")
    TravelAndPlaces = QT_TRANSLATE_NOOP("EmojiCategory", "Travel & Places")
    Flags = QT_TRANSLATE_NOOP("EmojiCategory", "Flags")


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
    emojiInserted = Signal(QEmojiCategoryItem, QEmojiItem)
    emojiRemoved = Signal(QEmojiCategoryItem, QEmojiItem)
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
            EmojiCategory.Recents: "fa6s.clock-rotate-left",
            EmojiCategory.Favorites: "fa6s.star",
            EmojiCategory.SmileysAndEmotion: "fa6s.face-smile",
            EmojiCategory.PeopleAndBody: "fa6s.user",
            EmojiCategory.AnimalsAndNature: "fa6s.leaf",
            EmojiCategory.FoodAndDrink: "fa6s.bowl-food",
            EmojiCategory.Symbols: "fa6s.heart",
            EmojiCategory.Activities: "fa6s.gamepad",
            EmojiCategory.Objects: "fa6s.lightbulb",
            EmojiCategory.TravelAndPlaces: "fa6s.bicycle",
            EmojiCategory.Flags: "fa6s.flag",
        }

        # 1. Add Categories in desired order (Standard Order + Specials)
        # Note: The order defined in EmojiCategory Enum or the loop below dictates display order
        # Adjust as needed. Here we follow a typical picker order.
        categories_order = [
            EmojiCategory.Recents,
            EmojiCategory.Favorites,
            EmojiCategory.SmileysAndEmotion,
            EmojiCategory.PeopleAndBody,
            EmojiCategory.AnimalsAndNature,
            EmojiCategory.FoodAndDrink,
            EmojiCategory.Activities,
            EmojiCategory.TravelAndPlaces,
            EmojiCategory.Objects,
            EmojiCategory.Symbols,
            EmojiCategory.Flags,
        ]

        for category in categories_order:
            if category == EmojiCategory.Recents and not self._recent_category:
                continue
            if category == EmojiCategory.Favorites and not self._favorite_category:
                continue

            icon = QThemeResponsiveIcon.fromAwesome(
                icons[category], options=[{"scale_factor": 0.9}]
            )
            self.addCategory(category, icon)

        # 2. Add Emojis
        for emoji_char in sorted(emoji_data, key=lambda e: e.sort_order):
            if emoji_char.category == "Component":
                continue

            self.addEmoji(emoji_char.category, emoji_char)

    def findEmojiInCategory(
        self, category_item: QEmojiCategoryItem, emoji: str
    ) -> typing.Optional[QEmojiItem]:
        """
        Find a specific emoji within a given category index.

        Args:
            category_item (QEmojiCategoryItem): The category to search in.
            emoji (str): The emoji character to find.

        Returns:
            Optional[QEmojiItem]: The found emoji item, or None if not found.
        """
        # match(start_index, role, value, hits, flags)
        # Search starting from the first child of the category
        start_index = self.index(0, 0, category_item.index())

        # We only want direct children, so we don't use Qt.MatchChange.MatchRecursive.
        matches = self.match(
            start_index,
            QEmojiItem.QEmojiDataRole.EmojiRole,
            emoji,
            1,  # Number of results (1 to stop at the first)
            Qt.MatchFlag.MatchExactly,
        )

        if matches:
            item = self.itemFromIndex(matches[0])
            if isinstance(item, QEmojiItem):
                return item
        return None

    def findEmojiInCategoryByName(
        self, category: typing.Union[str, EmojiCategory], emoji: str
    ) -> typing.Optional[QEmojiItem]:
        """
        Find a specific emoji within a given category by name.

        Args:
            category (Union[str, EmojiCategory]): The name or enum of the category to search in.
            emoji (str): The emoji character to find.

        Returns:
            Optional[QEmojiItem]: The found emoji item, or None if not found.
        """
        category_item = self.findCategory(category)
        if not category_item:
            return None
        return self.findEmojiInCategory(category_item, emoji)

    def findCategory(self, category_name: str) -> typing.Optional[QEmojiCategoryItem]:
        """
        Find a category by its name.

        Args:
            category_name (str): The name of the category to search for.

        Returns:
            Optional[QEmojiCategoryItem]: The category item, or None if not found.
        """
        start_index = self.index(0, 0)
        matches = self.match(
            start_index,
            QEmojiCategoryItem.QEmojiCategoryDataRole.CategoryRole,
            category_name,
            1,
            Qt.MatchFlag.MatchExactly,
        )
        if matches:
            item = self.itemFromIndex(matches[0])
            if isinstance(item, QEmojiCategoryItem):
                return item
        return None

    def setSkinTone(self, skin_tone: str):
        """
        Update the skin tone for all compatible emojis in the model.

        Iterates through tracked compatible emojis and updates their data with the new skin tone.

        Args:
            skin_tone (str): The new skin tone character/code.
        """
        for (
            category,
            emojis_with_skin_modifier,
        ) in self._emojis_skin_modifier_compatible.items():
            category_item = self.findCategory(category)
            if not category_item:
                return

            for emoji in emojis_with_skin_modifier:
                emoji_item = self.findEmojiInCategory(category_item, emoji)
                if not emoji_item:
                    continue

                emoji_item.setData(skin_tone, QEmojiItem.QEmojiDataRole.SkinToneRole)
                self.skinToneChanged.emit(emoji_item.index())

    def addCategory(self, name: str, icon: typing.Union[QIcon, QPixmap]) -> bool:
        """
        Add a new category to the model.

        Args:
            name (str): The name of the category.
            icon (Union[QIcon, QPixmap]): The icon for the category.

        Returns:
            bool: True if added, False if it already exists.
        """
        if self.findCategory(name):
            return False

        category_item = QEmojiCategoryItem(name, icon)
        self.appendRow(category_item)
        return True

    def removeCategory(self, name: str) -> bool:
        """
        Remove a category from the model.

        Args:
            name (str): The name of the category to remove.

        Returns:
            bool: True if removed, False if not found.
        """
        item = self.findCategory(name)
        if not item:
            return False

        self.removeRow(item.row())
        return True

    def addEmoji(self, category_name: str, emoji_char: EmojiChar) -> bool:
        """
        Add an emoji to a specific category.

        Args:
            category_name (str): The name of the category.
            emoji_char (EmojiChar): The emoji data object.

        Returns:
            bool: True if added, False if category not found or emoji already exists.
        """
        category_item = self.findCategory(category_name)
        if not category_item:
            return False

        if self.findEmojiInCategory(category_item, emoji_char.char):
            return False

        item = QEmojiItem(emoji_char)
        category_item.appendRow(item)

        # Update skin tone compatibility index if needed
        if QEmojiItem.skinToneCompatible(emoji_char):
            if category_name not in self._emojis_skin_modifier_compatible:
                self._emojis_skin_modifier_compatible[category_name] = []
            if (
                emoji_char.char
                not in self._emojis_skin_modifier_compatible[category_name]
            ):
                self._emojis_skin_modifier_compatible[category_name].append(
                    emoji_char.char
                )

        return True

    def removeEmoji(self, category_name: str, emoji_char: str) -> bool:
        """
        Remove an emoji from a specific category.

        Args:
            category_name (str): The name of the category.
            emoji_char (str): The emoji character string.

        Returns:
            bool: True if removed, False if not found.
        """
        category_item = self.findCategory(category_name)
        if not category_item:
            return False

        emoji_item = self.findEmojiInCategory(category_item, emoji_char)
        if not emoji_item:
            return False

        category_item.removeRow(emoji_item.row())

        return True

    @Slot(QModelIndex, int, int)
    def _on_rows_removed(self, parent: QModelIndex, first: int, last: int):
        """
        Handle internal slot for rows removed signal.

        Emits categoryRemoved signal when top-level rows (categories) are removed.
        Emits emojiRemoved signal when child rows (emojis) are removed.

        Args:
            parent (QModelIndex): The parent index.
            first (int): The first removed row.
            last (int): The last removed row.
        """
        if parent.isValid():
            parent_item = self.itemFromIndex(parent)
            if isinstance(parent_item, QEmojiCategoryItem):
                for row in range(first, last + 1):
                    # Since this is connected to rowsAboutToBeRemoved, the items still exist
                    child_index = self.index(row, 0, parent)
                    child_item = self.itemFromIndex(child_index)
                    if isinstance(child_item, QEmojiItem):
                        self.emojiRemoved.emit(parent_item, child_item)
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
        Emits emojiInserted signal when child rows (emojis) are added.

        Args:
            parent (QModelIndex): The parent index.
            first (int): The first inserted row.
            last (int): The last inserted row.
        """
        if parent.isValid():
            parent_item = self.itemFromIndex(parent)
            if isinstance(parent_item, QEmojiCategoryItem):
                for row in range(first, last + 1):
                    child_index = self.index(row, 0, parent)
                    child_item = self.itemFromIndex(child_index)
                    if isinstance(child_item, QEmojiItem):
                        self.emojiInserted.emit(parent_item, child_item)
            return

        for row in range(first, last + 1):
            item = self.item(row)
            if isinstance(item, QEmojiCategoryItem):
                self.categoryInserted.emit(item)
