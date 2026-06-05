import typing

from PySide6.QtGui import QStandardItem, Qt


class QAwesomeItem(QStandardItem):
    def __init__(self, name: str):
        super().__init__()
        self.setData(name, Qt.ItemDataRole.EditRole)
        self.setEditable(False)

    def data(self, /, role: int = Qt.ItemDataRole.EditRole) -> typing.Any:
        if role == Qt.ItemDataRole.UserRole:
            text = super().data(Qt.ItemDataRole.EditRole)
            return {text}

        return super().data(role)
