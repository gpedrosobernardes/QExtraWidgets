from PySide6.QtCore import QSortFilterProxyModel, QModelIndex
from qextrawidgets.widgets.emoji_picker.enums import QEmojiDataRole


class QEmojiSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self._category_filter = None
        self._favorite_filter = None
        self._recent_filter = None

    def setCategoryFilter(self, category_filter: str):
        self._category_filter = category_filter

    def setFavoriteFilter(self, favorite_filter: bool):
        self._favorite_filter = favorite_filter

    def setRecentFilter(self, recent_filter: bool):
        self._recent_filter = recent_filter

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex = ...):
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


