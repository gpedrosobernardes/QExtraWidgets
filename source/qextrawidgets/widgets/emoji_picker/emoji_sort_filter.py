import traceback
import typing
from functools import lru_cache

from PySide6.QtCore import QSortFilterProxyModel, QModelIndex
from PySide6.QtGui import QPixmap, Qt, QIcon
from PySide6.QtWidgets import QWidget

from qextrawidgets.widgets.emoji_picker.enums import QEmojiDataRole

"""Module providing QEmojiSortFilterProxyModel.

This module offers QEmojiSortFilterProxyModel — a QSortFilterProxyModel specialized
for emoji lists. It supports category, recent, and favorite filters and allows
supplying a callable pixmap getter for emoji decoration. The proxy converts
returned QPixmap to QIcon for consistent DecorationRole behavior and returns an
empty QIcon for invalid results.
"""


class QEmojiSortFilterProxyModel(QSortFilterProxyModel):
    """A proxy model for filtering and sorting emojis based on categories and other metadata."""

    def __init__(self, parent: QWidget = None) -> None:
        """Initializes the emoji proxy model.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._emoji_pixmap_getter = None

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

    def setEmojiPixmapGetter(self, emoji_pixmap_getter: typing.Optional[typing.Callable[[str], QPixmap]]) -> None:
        """Sets the function used to retrieve emoji pixmaps.

        This allows for custom emoji rendering (e.g., using Twemoji images).

        Args:
            emoji_pixmap_getter (Callable, optional): Pixmap getter function.
        """
        if emoji_pixmap_getter != self._emoji_pixmap_getter:
            self._emoji_pixmap_getter = emoji_pixmap_getter
            self._emoji_icon_getter.cache_clear()

    def emojiPixmapGetter(self) -> typing.Optional[typing.Callable[[str], QPixmap]]:
        """Returns the current emoji pixmap getter function."""
        return self._emoji_pixmap_getter

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> typing.Any:
        if not index.isValid():
            return None

        emoji_pixmap_getter = self.emojiPixmapGetter()

        # DecorationRole uses an int; comparing with int is more robust in PySide
        if role == int(Qt.ItemDataRole.DecorationRole):
            if not emoji_pixmap_getter:
                return QPixmap()

            try:
                source_index = self.mapToSource(index)
                if not source_index.isValid():
                    return QPixmap()

                emoji = source_index.data(Qt.ItemDataRole.EditRole)
                if emoji is None:
                    return QPixmap()

                return self._emoji_icon_getter(emoji)
            except Exception:
                # Evita crash no C++ propagando exceções; log para debug
                traceback.print_exc()
                return QPixmap()

        elif role == int(Qt.ItemDataRole.DisplayRole):
            source_index = self.mapToSource(index)

            if not source_index.isValid():
                return None

            if emoji_pixmap_getter:
                return ""

            return source_index.data(Qt.ItemDataRole.DisplayRole)

        return super().data(index, role)

    @lru_cache(maxsize=5120)
    def _emoji_icon_getter(self, emoji: str):
        emoji_pixmap_getter = self.emojiPixmapGetter()
        return QIcon(emoji_pixmap_getter(emoji))