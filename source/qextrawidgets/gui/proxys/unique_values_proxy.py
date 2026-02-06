import typing
from PySide6.QtCore import (
    QSortFilterProxyModel,
    QAbstractItemModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    QObject,
)


class QUniqueValuesProxyModel(QSortFilterProxyModel):
    """A proxy model that filters rows to show only unique values from a specific column.

    This is useful for creating filter lists where you want to show each available option exactly once,
    even if it appears multiple times in the source model.
    """

    def __init__(self, parent: typing.Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._target_column = 0
        self._unique_rows: typing.Set[int] = set()

    def setTargetColumn(self, column: int) -> None:
        """Sets the column to filter for unique values."""
        if self._target_column != column:
            self._target_column = column
            self.invalidateFilter()

    def targetColumn(self) -> int:
        return self._target_column

    def setSourceModel(self, source_model: QAbstractItemModel) -> None:
        super().setSourceModel(source_model)
        # Connect signals to invalidate cache on changes
        if source_model:
            # Connect using the correct signal signatures
            source_model.modelReset.connect(self.invalidateFilter)
            source_model.layoutChanged.connect(self.invalidateFilter)
            source_model.rowsInserted.connect(self.invalidateFilter)
            source_model.rowsRemoved.connect(self.invalidateFilter)
            source_model.dataChanged.connect(self.invalidateFilter)

        # Explicitly rebuild cache for the new model
        self.invalidateFilter()

    def filterAcceptsRow(
        self,
        source_row: int,
        source_parent: typing.Union[QModelIndex, QPersistentModelIndex],
    ) -> bool:
        """Accepts the row only if it's the first occurrence of its value."""
        # Note: QSortFilterProxyModel calls this method for every row.
        # We need to rely on the pre-calculated set of unique rows for performance.
        # If cache is empty and model is not, we might need to rebuild it?
        # Ideally, we rebuild cache in `invalidateFilter` or lazy load.
        # However, `filterAcceptsRow` is const and called during filtering.
        # We can't easily rebuild "once" inside here without flags.

        # Optimization: We check if this row is in our allowed set.
        return source_row in self._unique_rows

    def invalidateFilter(self) -> None:
        """Rebuilds the unique value cache and invalidates the filter."""
        self._rebuild_unique_cache()
        super().invalidate()

    def _rebuild_unique_cache(self) -> None:
        """Scans the source model and identifies the first row for each unique value."""
        self._unique_rows.clear()
        source = self.sourceModel()
        if not source:
            return

        seen_values = set()
        row_count = source.rowCount()

        for row in range(row_count):
            index = source.index(row, self._target_column)
            val = str(source.data(index, Qt.ItemDataRole.DisplayRole))

            if val not in seen_values:
                seen_values.add(val)
                self._unique_rows.add(row)

    def data(
        self,
        index: typing.Union[QModelIndex, QPersistentModelIndex],
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> typing.Any:
        # We might want to override data to potentially format stuff, but default proxy behavior is fine.
        return super().data(index, role)
