from PySide6.QtCore import QSortFilterProxyModel, QModelIndex
from PySide6.QtWidgets import QWidget
from qextrawidgets.widgets.emoji_picker.enums import QEmojiDataRole


class QEmojiSortFilterProxyModel(QSortFilterProxyModel):
    """A proxy model for filtering and sorting emojis based on categories and other metadata."""

    def __init__(self, parent: QWidget = None) -> None:
        """Initializes the emoji proxy model.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._category_filter = None
        self._favorite_filter = None
        self._recent_filter = None

    def setCategoryFilter(self, category_filter: str) -> None:
        """Sets the category to filter by.

        Args:
            category_filter (str): Category name.
        """
        self._category_filter = category_filter

    def setFavoriteFilter(self, favorite_filter: bool) -> None:
        """Sets whether to filter by favorite status.

        Args:
            favorite_filter (bool): True to show only favorites, False otherwise.
        """
        self._favorite_filter = favorite_filter

    def setRecentFilter(self, recent_filter: bool) -> None:
        """Sets whether to filter by recent status.

        Args:
            recent_filter (bool): True to show only recent emojis, False otherwise.
        """
        self._recent_filter = recent_filter

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Determines if a row should be accepted by the filter.

        Args:
            source_row (int): Row number in the source model.
            source_parent (QModelIndex): Parent index in the source model.

        Returns:
            bool: True if the row is accepted, False otherwise.
        """
        idx = self.sourceModel().index(source_row, 0, source_parent)
        aliases = idx.data(QEmojiDataRole.AliasRole)
        pattern = self.filterRegularExpression().pattern()
        if pattern and not pattern.lower() in aliases:
            return False
        category = idx.data(QEmojiDataRole.CategoryRole)
        if self._category_filter is not None and self._category_filter != category:
            return False
        recent = idx.data(QEmojiDataRole.RecentRole)
        if self._recent_filter is not None and self._recent_filter != recent:
            return False
        favorite = idx.data(QEmojiDataRole.FavoriteRole)
        if self._favorite_filter is not None and self._favorite_filter != favorite:
            return False
        return True


