import typing

from PySide6.QtGui import QStandardItem, QIcon, QPixmap, Qt


class QIconCategoryItem(QStandardItem):
    """
    A standard item representing a category of icons in the model.
    """
    def __init__(self, text: str, category: str, icon: typing.Union[QIcon, QPixmap]):
        """
        Initializes the category item.

        Args:
            category (str): The name of the category.
            icon (typing.Union[QIcon, QPixmap]): The icon representing the category.
        """
        super().__init__()
        self.setText(text)
        self.setIcon(icon)
        self.setData(category, Qt.ItemDataRole.UserRole)
        self.setEditable(False)

    def category(self) -> str:
        """
        Returns the category name.

        Returns:
            str: The category name.
        """
        return self.data(Qt.ItemDataRole.UserRole)
