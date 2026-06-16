import typing

from PySide6.QtCore import QModelIndex, QIdentityProxyModel, Qt
from PySide6.QtGui import QPixmap


class QDecorationProviderProxy(QIdentityProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._decoration_provider: typing.Optional[typing.Callable[[QModelIndex], QPixmap]] = None

    def setDecorationProvider(
            self,
            provider: typing.Callable[[QModelIndex], QPixmap]
    ) -> None:
        self._decoration_provider = provider

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DecorationRole):
        if role == Qt.ItemDataRole.DecorationRole:
            if self._decoration_provider is not None:
                return self._decoration_provider(index)
            return None
        return super().data(index, role)
