import typing

from PySide6.QtGui import QStandardItem, QIcon, QPixmap, Qt
from enum import Enum


class QEmojiCategoryItem(QStandardItem):

    class QEmojiCategoryDataRole(int, Enum):
        CategoryRole = Qt.ItemDataRole.UserRole + 2

    def __init__(self, category: str, icon: typing.Union[QIcon, QPixmap]):
        super().__init__()
        self.setText(category)
        self.setIcon(icon)
        self.setData(category, role=QEmojiCategoryItem.QEmojiCategoryDataRole.CategoryRole)
        self.setEditable(False)

    def category(self) -> str:
        return self.text()