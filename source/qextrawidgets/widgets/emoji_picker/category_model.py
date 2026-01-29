import typing

from PySide6.QtGui import QStandardItemModel, QIcon
from PySide6.QtWidgets import QWidget

from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.widgets.emoji_picker.category_item import QEmojiCategoryItem
from qextrawidgets.widgets.emoji_picker.enums import EmojiCategory


class QEmojiCategoryModel(QStandardItemModel):
    """A standard item model specialized for storing and managing emoji categories."""

    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        """Initializes the emoji category model.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._icons = {
            EmojiCategory.Activities: QThemeResponsiveIcon.fromAwesome("fa6s.gamepad", options=[{"scale_factor": 0.9}]),
            EmojiCategory.FoodAndDrink: QThemeResponsiveIcon.fromAwesome("fa6s.bowl-food"),
            EmojiCategory.AnimalsAndNature: QThemeResponsiveIcon.fromAwesome("fa6s.leaf"),
            EmojiCategory.PeopleAndBody: QThemeResponsiveIcon.fromAwesome("fa6s.user"),
            EmojiCategory.Symbols: QThemeResponsiveIcon.fromAwesome("fa6s.heart"),
            EmojiCategory.Flags: QThemeResponsiveIcon.fromAwesome("fa6s.flag"),
            EmojiCategory.TravelAndPlaces: QThemeResponsiveIcon.fromAwesome("fa6s.bicycle", options=[{"scale_factor": 0.9}]),
            EmojiCategory.Objects: QThemeResponsiveIcon.fromAwesome("fa6s.lightbulb"),
            EmojiCategory.SmileysAndEmotion: QThemeResponsiveIcon.fromAwesome("fa6s.face-smile"),
            EmojiCategory.Favorites: QThemeResponsiveIcon.fromAwesome("fa6s.star"),
            EmojiCategory.Recents: QThemeResponsiveIcon.fromAwesome("fa6s.clock-rotate-left")
        }

    def populate(self, favorite_category: bool = True, recent_category: bool = True) -> None:
        """Populates the model with standard emoji categories.

        Args:
            favorite_category (bool, optional): Whether to include the favorites category. Defaults to True.
            recent_category (bool, optional): Whether to include the recents category. Defaults to True.
        """
        self.clear()

        if favorite_category:
            self.addCategory(EmojiCategory.Favorites, EmojiCategory.Favorites, self._icons[EmojiCategory.Favorites])

        if recent_category:
            self.addCategory(EmojiCategory.Recents, EmojiCategory.Recents, self._icons[EmojiCategory.Recents])

        for category in sorted(EmojiCategory):
            if category not in (EmojiCategory.Favorites, EmojiCategory.Recents):
                self.addCategory(category, category, self._icons[category])

    def addCategory(self, category: str, text: str, icon: QIcon) -> None:
        """Adds a new category to the model.

        Args:
            category (str): The category identifier.
            text (str): The display text for the category.
            icon (QIcon): The icon for the category.
        """
        item = QEmojiCategoryItem(category, text, icon)
        self.appendRow(item)

    def insertCategory(self, index: int, category: str, text: str, icon: QIcon) -> None:
        """Inserts a new category at the specified index.

        Args:
            index (int): The index to insert the category at.
            category (str): The category identifier.
            text (str): The display text for the category.
            icon (QIcon): The icon for the category.
        """
        item = QEmojiCategoryItem(category, text, icon)
        self.insertRow(index, item)

    def removeCategory(self, category: str) -> None:
        """Removes a category from the model.

        Args:
            category (str): The category identifier to remove.
        """
        item = self.categoryItem(category)
        if item:
            self.removeRow(item.row())

    def categoryItem(self, category: str) -> typing.Optional[QEmojiCategoryItem]:
        """Finds and returns the item for a specific category.

        Args:
            category (str): The category identifier to search for.

        Returns:
            QEmojiCategoryItem, optional: The found item, or None.
        """
        for row in range(self.rowCount()):
            item = self.item(row)
            if isinstance(item, QEmojiCategoryItem) and item.category() == category:
                return item
        return None

    def getCategoryItems(self) -> typing.List[QEmojiCategoryItem]:
        """Returns a list of all category items in the model.

        Returns:
            List[QEmojiCategoryItem]: List of all items.
        """
        return [self.item(row) for row in range(self.rowCount()) if isinstance(self.item(row), QEmojiCategoryItem)]

    def setFavoriteCategory(self, active: bool) -> None:
        """Enables or disables the favorites category.

        Args:
            active (bool): True to enable, False to disable.
        """
        favorite_category_key = EmojiCategory.Favorites
        favorite_category = self.categoryItem(favorite_category_key)
        if favorite_category is not None and not active:
            self.removeCategory(favorite_category_key)
        elif favorite_category is None and active:
            self.insertCategory(0, favorite_category_key, favorite_category_key, self._icons[favorite_category_key])

    def setRecentCategory(self, active: bool) -> None:
        """Enables or disables the recents category.

        Args:
            active (bool): True to enable, False to disable.
        """
        recent_category_key = EmojiCategory.Recents
        recent_category = self.categoryItem(recent_category_key)
        if recent_category is not None and not active:
            self.removeCategory(recent_category_key)
        elif recent_category is None and active:
            # Insert after favorites if it exists, otherwise at 0
            index = 0
            if self.categoryItem(EmojiCategory.Favorites):
                index = 1
            self.insertCategory(index, recent_category_key, recent_category_key, self._icons[recent_category_key])
