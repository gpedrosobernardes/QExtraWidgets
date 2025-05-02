import typing

from PySide6.QtCore import QSortFilterProxyModel


class QMultiFilterProxy(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self._filters = {}

    def setFilter(self, col: int, text_list: typing.Iterable[str]):
        """Define a lista de filtros para uma coluna específica."""
        if text_list:
            self._filters[col] = text_list
        else:
            self._filters.pop(col, None)
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        """Verifica se a linha passa nos filtros."""
        model = self.sourceModel()
        for col, text_list in self._filters.items():
            index = model.index(source_row, col, source_parent)
            value = str(model.data(index))
            if not any(text in value for text in text_list):
                return False
        return True