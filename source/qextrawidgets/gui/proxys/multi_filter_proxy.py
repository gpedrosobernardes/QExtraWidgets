import typing

from PySide6.QtCore import QPersistentModelIndex
from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, QObject


class QMultiFilterProxyModel(QSortFilterProxyModel):
    """A proxy model that supports multiple filters per column."""

    def __init__(self, parent: typing.Optional[QObject] = None) -> None:
        """Initializes the multi-filter proxy model.

        Args:
            parent (QObject, optional): Parent object. Defaults to None.
        """
        super().__init__(parent)
        self._filters = {}

    def setFilter(
        self, col: int, text_list: typing.Optional[typing.Iterable[str]]
    ) -> None:
        """Sets the list of allowed values for a specific column.

        Args:
            col (int): Column index.
            text_list (Iterable[str], optional): List of allowed string values. If None or empty, the filter is removed.
        """
        if text_list:
            self._filters[col] = text_list
        else:
            self._filters.pop(col, None)
        self.invalidateFilter()

    def isFiltering(self) -> bool:
        """Returns True if any filter is active."""
        return bool(self._filters)

    def isColumnFiltered(self, col: int) -> bool:
        """Returns True if the given column is filtered."""
        return col in self._filters

    def filterAcceptsRow(
        self,
        source_row: int,
        source_parent: typing.Union[QModelIndex, QPersistentModelIndex],
    ) -> bool:
        """Determines if a row passes all column filters.

        Args:
            source_row (int): Row number.
            source_parent (QModelIndex): Parent index.

        Returns:
            bool: True if the row matches all filters, False otherwise.
        """
        model = self.sourceModel()
        if not model:
            return True

        for col, text_list in self._filters.items():
            index = model.index(source_row, col, source_parent)
            value = str(model.data(index))
            if not any(text == value for text in text_list):
                return False
        return True

    def reset(self):
        """Resets the filters."""
        self._filters = {}
        self.invalidateFilter()
