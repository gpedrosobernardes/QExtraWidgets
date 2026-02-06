import typing

from PySide6.QtGui import QStandardItem, QIcon, QPixmap, Qt
from enum import Enum


class QEmojiCategoryItem(QStandardItem):
    """
    A standard item representing a category of emojis in the model.
    """

    class QEmojiCategoryDataRole(int, Enum):
        """
        Custom data roles for the category item.
        """

        CategoryRole = Qt.ItemDataRole.UserRole + 2

    def __init__(self, category: str, icon: typing.Union[QIcon, QPixmap]):
        """
        Initializes the category item.

        Args:
            category (str): The name of the category.
            icon (typing.Union[QIcon, QPixmap]): The icon representing the category.
        """
        super().__init__()
        self.setText(category)
        self.setIcon(icon)
        self.setData(
            category, role=QEmojiCategoryItem.QEmojiCategoryDataRole.CategoryRole
        )
        self.setEditable(False)

    def category(self) -> str:
        """
        Returns the category name.

        Returns:
            str: The category name.
        """
        return self.text()
