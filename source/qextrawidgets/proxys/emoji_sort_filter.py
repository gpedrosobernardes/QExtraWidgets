from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, Qt


class EmojiSortFilterProxyModel(QSortFilterProxyModel):
    """A proxy model for filtering emojis based on their aliases stored in UserRole."""

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Determines if a row should be accepted by the filter.

        Expects a list of aliases in the UserRole data of the source model.

        Args:
            source_row (int): Row number.
            source_parent (QModelIndex): Parent index.

        Returns:
            bool: True if any alias matches the filter pattern, False otherwise.
        """
        idx = self.sourceModel().index(source_row, 0, source_parent)
        obj = idx.data(Qt.ItemDataRole.UserRole)
        if obj is None:
            return False
        aliases = obj[0]
        pattern = self.filterRegularExpression().pattern()
        if not pattern:
            return True
        return any(pattern.lower() in alias for alias in aliases)
