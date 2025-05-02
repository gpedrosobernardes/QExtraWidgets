from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, Qt


class EmojiSortFilterProxyModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex = ...):
        idx = self.sourceModel().index(source_row, 0, source_parent)
        obj = idx.data(Qt.ItemDataRole.UserRole)
        if obj is None:
            return False
        pattern = self.filterRegularExpression().pattern()
        if not pattern:
            return True
        return pattern.lower() in obj.aliases