import logging
import typing

from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, QPersistentModelIndex, Qt, Signal, Slot
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QWidget

from qextrawidgets.gui.items import QIconCategoryItem
from qextrawidgets.gui.items.icon_item import QIconItem
from qextrawidgets.gui.models.icon_picker_model import QIconPickerModel


class QIconPickerProxyModel(QSortFilterProxyModel):
    """
    A high-performance proxy model to filter icon by their alias.

    Optimizations:
    1. Uses setRecursiveFilteringEnabled(True) to avoid manual O(N^2) child iteration.
    2. Caches the search term to avoid repetitive string manipulations per row.
    """

    def __init__(self, parent: typing.Optional[QWidget] = None):
        """
        Initializes the QEmojiProxyModel.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setDynamicSortFilter(True)

        # [OPTIMIZATION]
        # Automatically shows the Category (Parent) if an Emoji (Child) matches.
        # This eliminates the need to manually iterate children in filterAcceptsRow.
        self.setRecursiveFilteringEnabled(True)

        # Cache for the prepared search term
        self._cached_pattern: str = ""

    def setFilterFixedString(self, pattern: str) -> None:
        """
        Overrides the base method to cache the lowercase pattern
        for faster comparison.
        """
        # Pre-calculate lower() once per keystroke, not once per row
        self._cached_pattern = pattern.lower() if pattern else ""
        super().setFilterFixedString(pattern)

    def filterAcceptsRow(self, source_row: int, source_parent: typing.Union[QModelIndex, QPersistentModelIndex]) -> bool:
        """
        Determines if a row should be included in the view.

        With recursive filtering enabled:
        - We only need to validate the leaf nodes (Emojis).
        - If we return True for an Emoji, its Category is auto-included.
        - If we return False for a Category, it is still shown if a child matches.
        """
        # If no filter, show everything
        if not self._cached_pattern:
            return True

        # [OPTIMIZATION]
        # If this is a Category (Root), we simply return False.
        # Why? Because setRecursiveFilteringEnabled(True) will force-show this
        # category later if any of its children return True.
        # This skips all logic for category rows.
        if not source_parent.isValid():
            return False

        # Get the index
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)

        # [OPTIMIZATION]
        # Fast string check using the cached pattern.
        # Python's 'in' operator is highly optimized for str.
        # We assume _cached_pattern is already lowercased in setFilterFixedString.

        # Check if case sensitivity is needed (rare for emoji pickers, but respecting the property)
        is_case_sensitive = self.filterCaseSensitivity() == Qt.CaseSensitivity.CaseSensitive
        search_term = self._cached_pattern if not is_case_sensitive else self.filterRegularExpression().pattern()

        # Retrieve Aliases
        # Note: Ensure your QEmojiItem returns a list of strings for this role
        aliases = index.data(Qt.ItemDataRole.UserRole)

        if aliases:
            for alias in aliases:
                # Clean alias (e.g., ":smile:" -> "smile") if needed, or check directly
                # Assuming alias data might have mixed case, we lower it only if insensitive
                alias_check = alias if is_case_sensitive else alias.lower()

                if search_term in alias_check:
                    return True

            return False
        else:
            icon_text = index.data(Qt.ItemDataRole.EditRole)

            if not icon_text:
                return False

            if search_term in icon_text:
                return True

            return False

    def itemFromIndex(self, index: QModelIndex) -> QStandardItem:
        source_index = self.mapToSource(index)
        return self.sourceModel().itemFromIndex(source_index)

    def sourceModel(self) -> QIconPickerModel:
        model = super().sourceModel()
        if isinstance(model, QIconPickerModel):
            return model
        else:
            raise ValueError("Source model is not defined!")
