import logging
import time
import typing
from enum import Enum, auto

import qtawesome
from PySide6.QtCore import Qt, QT_TRANSLATE_NOOP, QModelIndex, Slot, Signal
from PySide6.QtGui import QIcon, QPixmap, QStandardItemModel
from emoji_data_python import emoji_data

from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.gui.items import QIconCategoryItem
from qextrawidgets.gui.items.icon_item import QIconItem


class QIconPickerModel(QStandardItemModel):
    """
    Model for managing icons categories and items using QStandardItemModel.

    This model organizes icons into categories (e.g., Smileys & Emotion, Animals & Nature).

    Signals:
        categoryInserted (QIconCategoryItem): Emitted when a category is added.
        categoryRemoved (QIconCategoryItem): Emitted when a category is removed.
        iconInserted (QIconCategoryItem, QIconItem): Emitted when an icon is added.
        iconRemoved (QIconCategoryItem, QIconItem): Emitted when an icon is removed.
    """

    class BaseCategory(str, Enum):
        Recents = QT_TRANSLATE_NOOP("BaseCategory", "Recents")
        Favorites = QT_TRANSLATE_NOOP("BaseCategory", "Favorites")


    class EmojiCategory(str, Enum):
        """Standard emoji categories."""
        SmileysAndEmotion = QT_TRANSLATE_NOOP("EmojiCategory", "Smileys & Emotion")
        PeopleAndBody = QT_TRANSLATE_NOOP("EmojiCategory", "People & Body")
        AnimalsAndNature = QT_TRANSLATE_NOOP("EmojiCategory", "Animals & Nature")
        FoodAndDrink = QT_TRANSLATE_NOOP("EmojiCategory", "Food & Drink")
        Symbols = QT_TRANSLATE_NOOP("EmojiCategory", "Symbols")
        Activities = QT_TRANSLATE_NOOP("EmojiCategory", "Activities")
        Objects = QT_TRANSLATE_NOOP("EmojiCategory", "Objects")
        TravelAndPlaces = QT_TRANSLATE_NOOP("EmojiCategory", "Travel & Places")
        Flags = QT_TRANSLATE_NOOP("EmojiCategory", "Flags")


    class PopulateSource(int, Enum):
        Emojis = auto()
        AwesomeIcons = auto()

    categoryInserted = Signal(QIconCategoryItem)
    categoryRemoved = Signal(QIconCategoryItem)
    iconInserted = Signal(QIconCategoryItem, QIconItem)
    iconRemoved = Signal(QIconCategoryItem, QIconItem)
    colorChanged = Signal(QModelIndex)

    def __init__(self, populate_method: typing.Optional[QIconPickerModel.PopulateSource] = None):
        """
        Initialize the QIconPickerModel.
        """
        super().__init__()
        if populate_method:
            self.populate(populate_method)
        self.setup_connections()

    def setup_connections(self):
        self.rowsInserted.connect(self._on_rows_inserted)
        self.rowsAboutToBeRemoved.connect(self._on_rows_removed)

    @Slot(QModelIndex, int, int)
    def _on_rows_removed(self, parent: QModelIndex, first: int, last: int):
        """
        Handle internal slot for rows removed signal.

        Emits categoryRemoved signal when top-level rows (categories) are removed.
        Emits iconRemoved signal when child rows (icon) are removed.

        Args:
            parent (QModelIndex): The parent index.
            first (int): The first removed row.
            last (int): The last removed row.
        """
        if parent.isValid():
            parent_item = self.itemFromIndex(parent)

            if isinstance(parent_item, QIconCategoryItem):
                for row in range(first, last + 1):
                    # Since this is connected to rowsAboutToBeRemoved, the items still exist
                    child_index = self.index(row, 0, parent)
                    child_item = self.itemFromIndex(child_index)
                    if isinstance(child_item, QIconItem):
                        self.iconRemoved.emit(parent_item, child_item)
            return

        for row in range(first, last + 1):
            item = self.itemFromIndex(self.index(row, 0))
            if isinstance(item, QIconCategoryItem):
                self.categoryRemoved.emit(item)

    @Slot(QModelIndex, int, int)
    def _on_rows_inserted(self, parent: QModelIndex, first: int, last: int):
        """
        Handle internal slot for rows inserted signal.

        Emits categoryInserted signal when top-level rows (categories) are added.
        Emits iconInserted signal when child rows (icon) are added.

        Args:
            parent (QModelIndex): The parent index.
            first (int): The first inserted row.
            last (int): The last inserted row.
        """
        if parent.isValid():
            parent_item = self.itemFromIndex(parent)

            if isinstance(parent_item, QIconCategoryItem):
                for row in range(first, last + 1):
                    child_index = self.index(row, 0, parent)
                    child_item = self.itemFromIndex(child_index)
                    if isinstance(child_item, QIconItem):
                        self.iconInserted.emit(parent_item, child_item)
            return

        for row in range(first, last + 1):
            item = self.itemFromIndex(self.index(row, 0))
            if isinstance(item, QIconCategoryItem):
                self.categoryInserted.emit(item)

    def populate(self,
                 source: QIconPickerModel.PopulateSource,
                 recent_category: bool = True,
                 favorite_category: bool = True,
                 ignored_categories: typing.Optional[typing.List[str]] = None) -> None:
        """
        Populates the model with the specified method and base categories if required.

        Args:
            source: Source used to populate the model.
            recent_category: Append recent categories if True.
            favorite_category: Append favorite categories if True.
            ignored_categories: Categories to ignore.

        Returns:
            None
        """
        self.populate_base_categories(recent_category, favorite_category)

        if source == QIconPickerModel.PopulateSource.Emojis:
            self.populate_with_emoji_icons(ignored_categories)
        elif source == QIconPickerModel.PopulateSource.AwesomeIcons:
            self.populate_with_awesome_icons(ignored_categories)

    def populate_base_categories(self, recent_category: bool = True, favorite_category: bool = True) -> None:
        """
        Populate the base categories, recent and favorite categories.

        Args:
            recent_category: Append recent categories if True.
            favorite_category: Append favorite categories if True.

        Returns:
            None
        """

        if recent_category:
            icon = QThemeResponsiveIcon.fromAwesome(
                "fa6s.clock-rotate-left", options=[{"scale_factor": 0.9}]
            )
            self.addCategory(QIconPickerModel.BaseCategory.Recents, QIconPickerModel.BaseCategory.Recents, icon)
        if favorite_category:
            icon = QThemeResponsiveIcon.fromAwesome(
                "fa6s.star", options=[{"scale_factor": 0.9}]
            )
            self.addCategory(QIconPickerModel.BaseCategory.Favorites, QIconPickerModel.BaseCategory.Favorites, icon)

    # noinspection PyProtectedMember
    def populate_with_awesome_icons(self, ignored_categories: typing.Optional[typing.List[str]] = None) -> None:
        """
        Populates the model with icons from 'qtawesome' package.

        Args:
            ignored_categories: Categories to ignore.

        Returns:
            None
        """
        qtawesome._instance()
        font_maps = qtawesome._resource["iconic"].charmap
        font_names = qtawesome._resource["iconic"].fontname

        icons = {
            "fa5": "fa5.font-awesome-logo-full",
            "fa5s": "fa5s.font-awesome-logo-full",
            "fa5b": "fa5b.font-awesome-flag",
            "fa6": "fa6.font-awesome",
            "fa6s": "fa6s.font-awesome",
            "fa6b": "fa6b.font-awesome",
            "mdi": "mdi.material-design",
            "mdi6": "mdi6.material-design",
            "ei": "ei.redux",
            "ph": "ph.phosphor-logo",
            "ri": "ri.remixicon-fill",
            "msc": "mdi.microsoft-visual-studio"
        }

        if ignored_categories is None:
            ignored_categories = []

        for font_collection, font_data in font_maps.items():
            if font_collection not in ignored_categories:
                font_name = font_names[font_collection]
                self.addCategory(font_name, font_collection, QThemeResponsiveIcon.fromAwesome(icons[font_collection]))

                for icon_name in font_data:
                    item = QIconItem(f"{font_collection}.{icon_name}", True)
                    self.addIcon(font_collection, item)

    def populate_with_emoji_icons(self, ignored_categories: typing.Optional[typing.List[str]] = None):
        """
        Populate the model with emoji categories and items.

        Iterates through the emoji database, groups emojis by category, and creates the hierarchical model structure.
        Compatible emojis are tracked for skin tone updates.
        """
        if ignored_categories is None:
            ignored_categories = []

        icons = {
            QIconPickerModel.EmojiCategory.SmileysAndEmotion: "fa6s.face-smile",
            QIconPickerModel.EmojiCategory.PeopleAndBody: "fa6s.user",
            QIconPickerModel.EmojiCategory.AnimalsAndNature: "fa6s.leaf",
            QIconPickerModel.EmojiCategory.FoodAndDrink: "fa6s.bowl-food",
            QIconPickerModel.EmojiCategory.Symbols: "fa6s.heart",
            QIconPickerModel.EmojiCategory.Activities: "fa6s.gamepad",
            QIconPickerModel.EmojiCategory.Objects: "fa6s.lightbulb",
            QIconPickerModel.EmojiCategory.TravelAndPlaces: "fa6s.bicycle",
            QIconPickerModel.EmojiCategory.Flags: "fa6s.flag",
        }

        # 1. Add Categories in desired order (Standard Order + Specials)
        # Note: The order defined in EmojiCategory Enum or the loop below dictates display order
        # Adjust as needed. Here we follow a typical picker order.
        categories_order = [
            QIconPickerModel.EmojiCategory.SmileysAndEmotion,
            QIconPickerModel.EmojiCategory.PeopleAndBody,
            QIconPickerModel.EmojiCategory.AnimalsAndNature,
            QIconPickerModel.EmojiCategory.FoodAndDrink,
            QIconPickerModel.EmojiCategory.Activities,
            QIconPickerModel.EmojiCategory.TravelAndPlaces,
            QIconPickerModel.EmojiCategory.Objects,
            QIconPickerModel.EmojiCategory.Symbols,
            QIconPickerModel.EmojiCategory.Flags,
        ]

        for category in categories_order:
            if category not in ignored_categories:
                icon = QThemeResponsiveIcon.fromAwesome(
                    icons[category], options=[{"scale_factor": 0.9}]
                )
                self.addCategory(category, category, icon)

        # 2. Add Emojis
        for emoji_char in sorted(emoji_data, key=lambda e: e.sort_order):
            if emoji_char.category == "Component" or emoji_char.category in ignored_categories:
                continue

            self.addIcon(emoji_char.category, QIconItem.fromEmojiChar(emoji_char))

    def findIconInCategory(
        self, category_item: QIconCategoryItem, icon_text: str
    ) -> typing.Optional[QIconItem]:
        """
        Find a specific icon within a given category index.

        Args:
            category_item (QIconCategoryItem): The category to search in.
            icon_text (str): The icon to find.

        Returns:
            Optional[QIconItem]: The found icon item, or None if not found.
        """
        # match(start_index, role, value, hits, flags)
        # Search starting from the first child of the category
        start_index = self.index(0, 0, category_item.index())

        # We only want direct children, so we don't use Qt.MatchChange.MatchRecursive.
        matches = self.match(
            start_index,
            Qt.ItemDataRole.EditRole,
            icon_text,
            1,  # Number of results (1 to stop at the first)
            Qt.MatchFlag.MatchExactly,
        )

        if matches:
            item = self.itemFromIndex(matches[0])
            if isinstance(item, QIconItem):
                return item
        return None

    def findIconInCategoryByName(
        self, category: str, icon_text: str
    ) -> typing.Optional[QIconItem]:
        """
        Find a specific icon within a given category by name.

        Args:
            category (str): The name of the category to search in.
            icon_text (str): The icon to find.

        Returns:
            Optional[QIconItem]: The found icon item, or None if not found.
        """
        category_item = self.findCategory(category)
        if not category_item:
            return None
        return self.findIconInCategory(category_item, icon_text)

    def findCategory(self, category_name: str) -> typing.Optional[QIconCategoryItem]:
        """
        Find a category by its name.

        Args:
            category_name (str): The name of the category to search for.

        Returns:
            Optional[QIconCategoryItem]: The category item, or None if not found.
        """
        start_index = self.index(0, 0)
        matches = self.match(
            start_index,
            Qt.ItemDataRole.UserRole,
            category_name,
            1,
            Qt.MatchFlag.MatchExactly,
        )
        if matches:
            item = self.itemFromIndex(matches[0])
            if isinstance(item, QIconCategoryItem):
                return item
        return None

    def addCategory(self, text: str, name: str, icon: typing.Union[QIcon, QPixmap]) -> bool:
        """
        Add a new category to the model.

        Args:
            text:
            name (str): The name of the category.
            icon (Union[QIcon, QPixmap]): The icon for the category.

        Returns:
            bool: True if added, False if it already exists.
        """
        if self.findCategory(name):
            return False

        category_item = QIconCategoryItem(text, name, icon)
        self.appendRow(category_item)
        return True

    def categories(self) -> typing.List[QIconCategoryItem]:
        """
        Get all category items in the model.

        Returns:
            List[QIconCategoryItem]: A list of all icon category items.
        """
        category_items = []
        for row in range(self.rowCount()):
            item = self.item(row)
            if isinstance(item, QIconCategoryItem):
                category_items.append(item)
        return category_items

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

    def addIcon(self, category_name: str, item: QIconItem) -> bool:
        """
        Add an icon to a specific category.

        Args:
            category_name (str): The name of the category.
            item (QIconItem): The icon item to add.

        Returns:
            bool: True if added, False if category not found or icon already exists.
        """
        category_item = self.findCategory(category_name)
        if not category_item:
            return False

        icon_text = item.data(Qt.ItemDataRole.EditRole)
        if self.findIconInCategory(category_item, icon_text):
            return False

        category_item.appendRow(item)

        return True

    def removeIcon(self, category_name: str, icon_text: str) -> bool:
        """
        Remove an icon from a specific category.

        Args:
            category_name (str): The name of the category.
            icon_text (str): The icon character string.

        Returns:
            bool: True if removed, False if not found.
        """
        category_item = self.findCategory(category_name)
        if not category_item:
            return False

        icon_item = self.findIconInCategory(category_item, icon_text)
        if not icon_item:
            return False

        category_item.removeRow(icon_item.row())

        return True

    def setColorModifier(self, color_modifier: str) -> None:
        """
        Applies a color modifier to each QIconItem in the model. Emits the color modifier role.

        Args:
            color_modifier: The color modifier to apply.

        Returns:
            None
        """

        start = time.perf_counter()

        for row in range(self.rowCount()):
            category_item = self.item(row)

            if not isinstance(category_item, QIconCategoryItem):
                continue

            for child_row in range(category_item.rowCount()):
                item = category_item.child(child_row)

                if isinstance(item, QIconItem) and item.data(QIconItem.QIconItemDataRole.SupportColorModifier):
                    item.setData(color_modifier, QIconItem.QIconItemDataRole.ColorModifierRole)
                    self.colorChanged.emit(item.index())
                    logging.debug("Defined ColorModifierRole for {}".format(item.data(Qt.ItemDataRole.EditRole)))

        end = time.perf_counter()
        logging.debug(f"Finished setColorModifier in {end - start:.6f} seconds.")
