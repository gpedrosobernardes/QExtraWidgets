import typing

from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtWidgets import QWidget

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

        self._alias_key = None

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
        self._cached_pattern = pattern.casefold()
        super().setFilterFixedString(pattern)

    def filterAcceptsRow(self, source_row: int, source_parent: typing.Union[QModelIndex, QPersistentModelIndex]) -> bool:
        """
        Determines if a row should be included in the view.

        With recursive filtering enabled:
        - We only need to validate the leaf nodes (Emojis).
        - If we return True for an Emoji, its Category is auto-included.
        - If we return False for a Category, it is still shown if a child matches.
        """
        if not self._cached_pattern:
            return True

        if not source_parent.isValid():
            return False

        # Get the index
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)

        is_case_sensitive = self.filterCaseSensitivity() == Qt.CaseSensitivity.CaseSensitive
        pattern = self.filterRegularExpression().pattern()

        aliases = index.data(Qt.ItemDataRole.UserRole)
        if is_case_sensitive:
            return any(pattern in alias for alias in aliases)
        else:
            return any(self._cached_pattern in alias.casefold() for alias in aliases)

    def sourceModel(self) -> QIconPickerModel:
        """
        Getter for source model. Override the original method to return a QIconPickerModel.

        Returns:
            QIconPickerModel
        """
        model = super().sourceModel()
        if isinstance(model, QIconPickerModel):
            return model
        else:
            raise ValueError("Source model is not defined!")