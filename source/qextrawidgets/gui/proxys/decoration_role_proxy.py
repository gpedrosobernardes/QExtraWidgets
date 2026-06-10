import typing

from PySide6.QtCore import (
    QIdentityProxyModel,
    Qt,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
)


class QDecorationRoleProxyModel(QIdentityProxyModel):
    """A proxy model that stores decoration data internally, without modifying the source model.

    This is useful for views where you need to display icons or colors
    without affecting the underlying data.
    """

    def __init__(self, parent: typing.Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._decorations: typing.Dict[QPersistentModelIndex, typing.Any] = {}
        self._default_decoration: typing.Any = None

    def data(
        self,
        index: typing.Union[QModelIndex, QPersistentModelIndex],
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> typing.Any:
        """Returns the data for the given index and role."""
        if role == Qt.ItemDataRole.DecorationRole:
            persistent_index = QPersistentModelIndex(index)
            try:
                decoration = self._decorations[persistent_index]
            except KeyError:
                return super().data(index, Qt.ItemDataRole.DecorationRole)
            else:
                return decoration

        return super().data(index, role)

    def setData(
        self,
        index: typing.Union[QModelIndex, QPersistentModelIndex],
        value: typing.Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        """Sets the data for the given index and role."""
        if role == Qt.ItemDataRole.DecorationRole:
            if not index.isValid():
                return False

            persistent_index = QPersistentModelIndex(index)
            self._decorations[persistent_index] = value
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DecorationRole])
            return True

        return super().setData(index, value, role)

    def clearDecorations(self) -> None:
        """Clears all explicit decorations, reverting to the default."""
        self._decorations.clear()
        if self.sourceModel():
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(
                    self.sourceModel().rowCount() - 1,
                    self.sourceModel().columnCount() - 1,
                ),
                [Qt.ItemDataRole.DecorationRole],
            )
