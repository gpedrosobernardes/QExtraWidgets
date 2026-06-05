import typing
from enum import Enum

from PySide6.QtCore import Qt, QT_TRANSLATE_NOOP, Signal, QModelIndex
from PySide6.QtGui import QIcon, QPixmap, QStandardItemModel, QStandardItem

from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.gui.items import QIconCategoryItem


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

    categoryInserted = Signal(QIconCategoryItem)
    categoryRemoved = Signal(QIconCategoryItem)
    iconInserted = Signal(QIconCategoryItem, QStandardItem)
    iconRemoved = Signal(QIconCategoryItem, QStandardItem)
    requestIcon = Signal(QModelIndex)

    def __init__(self,
                 parent = None,
                 recent_category: bool = True,
                 favorite_category: bool = True,
                 ignored_categories: typing.Optional[typing.List[str]] = None):
        """
        Initialize the QIconPickerModel.
        """
        super().__init__(parent)
        self.populate(recent_category, favorite_category, ignored_categories)

    def populate(self,
                 recent_category: bool = True,
                 favorite_category: bool = True,
                 ignored_categories: typing.Optional[typing.List[str]] = None) -> None:
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

    def findIconInCategory(
        self, category_item: QStandardItem, icon_text: str
    ) -> typing.Optional[QStandardItem]:
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
            return self.itemFromIndex(matches[0])
        return None

    def findIconInCategoryByName(
        self, category: str, icon_text: str
    ) -> typing.Optional[QStandardItem]:
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

    def findCategory(self, category_name: str) -> typing.Optional[QStandardItem]:
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
            return self.itemFromIndex(matches[0])
        return None

    def addCategory(self, text: str, name: str, icon: typing.Union[QIcon, QPixmap]) -> QIconCategoryItem:
        """
        Add a new category to the model.

        Args:
            text:
            name (str): The name of the category.
            icon (Union[QIcon, QPixmap]): The icon for the category.

        Returns:
            bool: True if added, False if it already exists.
        """
        category_item = QIconCategoryItem(text, name, icon)
        self.appendRow(category_item)
        return category_item

    def categories(self) -> typing.List[QStandardItem]:
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

    def addIcon(self, category_name: str, item: QStandardItem) -> bool:
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
