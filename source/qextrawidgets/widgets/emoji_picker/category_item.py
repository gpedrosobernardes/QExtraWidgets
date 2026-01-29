import typing

from PySide6.QtGui import QStandardItem, QIcon

from qextrawidgets.widgets.emoji_picker.enums import QEmojiDataRole


class QEmojiCategoryItem(QStandardItem):
    """A standard item representing a category in the emoji picker."""

    def __init__(self, category: str, text: str, icon: QIcon):
        """Initializes the category item.

        Args:
            category (str): The category identifier.
            text (str): The display text for the category.
            icon (QIcon): The icon for the category.
        """
        super().__init__(text)
        self.setIcon(icon)
        self.setData(category, QEmojiDataRole.CategoryRole)

    def category(self) -> str:
        """Returns the category identifier.

        Returns:
            str: The category identifier.
        """
        return self.data(QEmojiDataRole.CategoryRole)
