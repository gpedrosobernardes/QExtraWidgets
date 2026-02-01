from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, Qt
from PySide6.QtWidgets import QWidget
from typing import Optional

from qextrawidgets.items.emoji_item import QEmojiDataRole


class QEmojiPickerProxyModel(QSortFilterProxyModel):
    """
    A proxy model to filter emojis by their alias while preserving the category structure.

    This proxy ensures that if an emoji matches the filter, its parent category
    remains visible.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initializes the QEmojiProxyModel.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        # Ensure the proxy re-evaluates when data changes
        self.setDynamicSortFilter(True)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """
        Determines if a row should be included in the view.

        Args:
            source_row (int): The row index in the source model.
            source_parent (QModelIndex): The parent index in the source model.

        Returns:
            bool: True if the row should be visible, False otherwise.
        """
        model = self.sourceModel()
        if not model:
            return False

        index = model.index(source_row, 0, source_parent)

        # Get the filter pattern
        # We use the regex pattern directly to support the standard setFilterFixedString
        # or setFilterRegularExpression methods of the base class.
        pattern = self.filterRegularExpression().pattern()

        if not pattern:
            return True

        # Check if the current index is a Category (Root level, has no parent)
        if not source_parent.isValid():
            return self._accepts_category(index, pattern)

        # Check if the current index is an Item (Leaf level)
        return self._accepts_item(index, pattern)

    def _accepts_item(self, index: QModelIndex, pattern: str) -> bool:
        """
        Checks if an emoji item matches the filter pattern via its aliases.

        Args:
            index (QModelIndex): The index of the emoji item.
            pattern (str): The regex pattern or search string.

        Returns:
            bool: True if the item matches.
        """
        aliases = index.data(QEmojiDataRole.AliasRole)

        if not aliases:
            return False

        # If strict regex is needed, we would compile it.
        # However, for typical 'search', a case-insensitive 'contains' check on the pattern is often expected
        # if using setFilterFixedString. The QSortFilterProxyModel regex is already set up.
        # We assume simple substring matching for performance if the pattern is simple text.

        # Note: pattern coming from filterRegularExpression().pattern() might handle casing
        # depending on setFilterCaseSensitivity logic, but here we do manual check
        # because the data is a List[str], not a single string role.

        search_term = pattern.lower() if self.filterCaseSensitivity() == Qt.CaseSensitivity.CaseInsensitive else pattern

        for alias in aliases:
            alias_to_check = alias.lower() if self.filterCaseSensitivity() == Qt.CaseSensitivity.CaseInsensitive else alias

            if search_term in alias_to_check:
                return True

        return False

    def _accepts_category(self, category_index: QModelIndex, pattern: str) -> bool:
        """
        Checks if a category contains any children that match the filter.

        Args:
            category_index (QModelIndex): The index of the category.
            pattern (str): The search pattern.

        Returns:
            bool: True if at least one child matches.
        """
        model = self.sourceModel()
        row_count = model.rowCount(category_index)

        for i in range(row_count):
            child_index = model.index(i, 0, category_index)
            if self._accepts_item(child_index, pattern):
                return True

        return False