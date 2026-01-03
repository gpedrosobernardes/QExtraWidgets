import typing

from PySide6.QtCore import QSortFilterProxyModel


class QMultiFilterProxy(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self._filters = {}

    def setFilter(self, col: int, text_list: typing.Iterable[str]):
        """Sets the list of filters for a specific column."""
        if text_list:
            self._filters[col] = text_list
        else:
            self._filters.pop(col, None)
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        """Checks if the row passes the filters."""
        model = self.sourceModel()
        for col, text_list in self._filters.items():
            index = model.index(source_row, col, source_parent)
            value = str(model.data(index))
            if not any(text in value for text in text_list):
                return False
        return True
