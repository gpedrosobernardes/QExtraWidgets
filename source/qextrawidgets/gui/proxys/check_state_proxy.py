import typing

from PySide6.QtCore import (
    QIdentityProxyModel,
    Qt,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
)


class QCheckStateProxyModel(QIdentityProxyModel):
    """A proxy model that stores check states internally, without modifying the source model.

    This is useful for views where the user needs to select items (e.g., for filtering)
    without affecting the selection state of the underlying data.
    """

    def __init__(self, parent: typing.Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._checks: typing.Dict[QPersistentModelIndex, Qt.CheckState] = {}
        self._default_check_state = Qt.CheckState.Unchecked

    def flags(
        self, index: typing.Union[QModelIndex, QPersistentModelIndex]
    ) -> Qt.ItemFlag:
        """Returns the item flags for the given index, ensuring it is checkable."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        flags = super().flags(index)
        return flags | Qt.ItemFlag.ItemIsUserCheckable

    def data(
        self,
        index: typing.Union[QModelIndex, QPersistentModelIndex],
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> typing.Any:
        """Returns the data for the given index and role."""
        if role == Qt.ItemDataRole.CheckStateRole:
            if index.isValid():
                persistent_index = QPersistentModelIndex(index)
                return self._checks.get(persistent_index, self._default_check_state)
            return None

        return super().data(index, role)

    def setData(
        self,
        index: typing.Union[QModelIndex, QPersistentModelIndex],
        value: typing.Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        """Sets the data for the given index and role."""
        if role == Qt.ItemDataRole.CheckStateRole:
            if not index.isValid():
                return False

            persistent_index = QPersistentModelIndex(index)
            self._checks[persistent_index] = value
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
            return True

        return super().setData(index, value, role)

    def setInitialCheckState(self, state: Qt.CheckState) -> None:
        """Sets the default check state for all items not explicitly set."""
        self._default_check_state = state
        # Invalidate all data to refresh the view
        if self.sourceModel():
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(
                    self.sourceModel().rowCount() - 1,
                    self.sourceModel().columnCount() - 1,
                ),
                [Qt.ItemDataRole.CheckStateRole],
            )

    def setAllCheckState(self, state: Qt.CheckState) -> None:
        """Sets the check state for all items in the model."""
        self._checks.clear()
        self.setInitialCheckState(state)

    def getCheckedRows(self, column: int = 0) -> typing.Set[int]:
        """Returns a set of row numbers that are currently checked."""
        checked_rows = set()
        model = self.sourceModel()
        if not model:
            return checked_rows

        # Iterate over all rows to check their state
        # Note: This checks the effective state (explicit or default)
        for row in range(model.rowCount()):
            index = self.index(row, column)
            if (
                self.data(index, Qt.ItemDataRole.CheckStateRole)
                == Qt.CheckState.Checked
            ):
                checked_rows.add(row)

        return checked_rows
