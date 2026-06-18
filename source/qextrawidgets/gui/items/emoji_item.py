import typing

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from emoji_data_python import EmojiChar

from qextrawidgets.core.utils.emojis import QEmojiUtils


class QEmojiItem(QStandardItem):
    def __init__(self, emoji_char: EmojiChar) -> None:
        super().__init__()
        self.setData(emoji_char, Qt.ItemDataRole.EditRole)
        self.setEditable(False)

    def data(self, /, role: int = Qt.ItemDataRole.EditRole) -> typing.Any:
        if role == Qt.ItemDataRole.UserRole:
            emoji_char = super(QEmojiItem, self).data(Qt.ItemDataRole.EditRole)
            short_names = QEmojiUtils.ensureGetEmojiCharVariable(emoji_char, "short_names")
            return set(short_names)

        elif role == Qt.ItemDataRole.DecorationRole:
            emoji_char = super(QEmojiItem, self).data(Qt.ItemDataRole.EditRole)
            return emoji_char.char

        elif role == Qt.ItemDataRole.ToolTipRole:
            emoji_char = super(QEmojiItem, self).data(Qt.ItemDataRole.EditRole)
            name = QEmojiUtils.ensureGetEmojiCharVariable(emoji_char, "name")
            return name.title()

        return super(QEmojiItem, self).data(role)

    def clone(self, /):
        return QEmojiItem(self.data(Qt.ItemDataRole.EditRole))