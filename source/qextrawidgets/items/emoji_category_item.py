import typing

from PySide6.QtGui import QStandardItem, QIcon, QPixmap

from qextrawidgets.items.emoji_item import QEmojiDataRole
from qextrawidgets.views.grouped_icon_view import QGroupedIconView


class QEmojiCategoryItem(QStandardItem):
    def __init__(self, category: str, icon: typing.Union[QIcon, QPixmap]):
        super().__init__()
        self.setText(category)
        self.setIcon(icon)
        self.setData(False, role=QGroupedIconView.ExpansionStateRole)
        self.setData(category, role=QEmojiDataRole.CategoryRole)
        self.setEditable(False)

    def category(self) -> str:
        return self.text()