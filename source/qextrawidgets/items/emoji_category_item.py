import typing

from PySide6.QtGui import QStandardItem, QIcon, QPixmap, Qt

from qextrawidgets.items.emoji_item import QEmojiDataRole


class QEmojiCategoryItem(QStandardItem):
    ExpansionStateRole = Qt.ItemDataRole.UserRole + 100

    def __init__(self, category: str, icon: typing.Union[QIcon, QPixmap]):
        super().__init__()
        self.setText(category)
        self.setIcon(icon)
        self.setData(False, role=self.ExpansionStateRole)
        self.setData(category, role=QEmojiDataRole.CategoryRole)
        self.setEditable(False)

    def category(self) -> str:
        return self.text()