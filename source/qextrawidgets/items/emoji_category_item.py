import typing

from PySide6.QtGui import QStandardItem, QIcon, QPixmap


class QEmojiCategoryItem(QStandardItem):
    def __init__(self, category: str, icon: typing.Union[QIcon, QPixmap]):
        super().__init__()
        self.setText(category)
        self.setIcon(icon)
        self.setEditable(False)

    def category(self) -> str:
        return self.text()