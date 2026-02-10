from typing import Callable, Dict, Optional, Any
from PySide6.QtCore import QIdentityProxyModel, QModelIndex, Qt


class QFormatProxyModel(QIdentityProxyModel):
    """Proxy model that acts as a visual translator applying formatting masks to specific columns.

    The class keeps the original data intact for editing and calculations,
    applying formatting only when the View requests data for display (DisplayRole).

    Example:
        proxy = FormatProxyModel()
        proxy.setSourceModel(source_model)

        # Formatter for currency values
        def format_currency(value):
            return f"R$ {value:,.2f}"

        # Register formatter on column 2
        proxy.setColumnFormatter(2, format_currency)

        table_view.setModel(proxy)
    """

    def __init__(self, parent: Optional[Any] = None) -> None:
        """Initializes the FormatProxyModel.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)

        # Dictionary mapping column index to formatting function
        self._column_formatters: Dict[int, Callable[[Any], str]] = {}

    def setColumnFormatter(
        self, column: int, formatter: Optional[Callable[[Any], str]]
    ) -> None:
        """Registers or updates the formatting function for a specific column.

        Args:
            column: Column index (0-based).
            formatter: Callable that receives the raw value and returns the formatted string.
                      If None, removes the formatter from the column.

        Example:
            # Add formatter
            proxy.setColumnFormatter(0, lambda x: f"{x:04d}")

            # Remove formatter
            proxy.setColumnFormatter(0, None)
        """
        # If formatter is None, remove existing formatter
        if formatter is None:
            if column in self._column_formatters:
                del self._column_formatters[column]
        else:
            # Register or update the formatter
            self._column_formatters[column] = formatter

        # Emit dataChanged to update the View
        # Notify that all items in the column need to be redrawn
        if self.sourceModel() is not None:
            row_count = self.rowCount()
            if row_count > 0:
                top_left = self.index(0, column)
                bottom_right = self.index(row_count - 1, column)
                self.dataChanged.emit(
                    top_left, bottom_right, [Qt.ItemDataRole.DisplayRole]
                )

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Intercepts data requests to apply visual formatting.

        Formatting is applied only when:
        1. The requested role is DisplayRole
        2. The index column has a registered formatter

        For all other cases, delegates to the superclass implementation.

        Args:
            index: Index of the item in the model.
            role: Role defining the type of data requested.

        Returns:
            Formatted data (if DisplayRole and column has formatter),
            or original data from superclass.
        """
        # Check if interception should occur
        if not index.isValid():
            return super().data(index, role)

        column = index.column()

        # Intercept only DisplayRole for columns with registered formatter
        if role == Qt.ItemDataRole.DisplayRole and column in self._column_formatters:
            # Map proxy index to source model
            source_index = self.mapToSource(index)

            if not source_index.isValid():
                return super().data(index, role)

            # Extract raw data, prioritizing EditRole (unformatted data)
            # EditRole ensures we get the real value, not an already formatted version
            source_model = self.sourceModel()
            raw_data = source_model.data(source_index, Qt.ItemDataRole.EditRole)

            # Fallback to DisplayRole if EditRole returns None
            if raw_data is None:
                raw_data = source_model.data(source_index, Qt.ItemDataRole.DisplayRole)

            # If still no data, return None
            if raw_data is None:
                return None

            # Apply formatter with exception protection
            try:
                formatter = self._column_formatters[column]
                formatted_value = formatter(raw_data)
                return formatted_value
            except Exception:
                # On formatter error, return raw data as string
                # This prevents the application from breaking due to formatting function errors
                return str(raw_data)

        # For any other role or columns without formatter,
        # delegate to superclass implementation
        return super().data(index, role)

    def columnFormatter(self, column: int) -> Optional[Callable[[Any], str]]:
        """Returns the registered formatter for a specific column.

        Args:
            column: Column index.

        Returns:
            Formatter callable or None if no formatter is registered.
        """
        return self._column_formatters.get(column)

    def clearAllFormatters(self) -> None:
        """Removes all registered formatters and updates the View."""
        if not self._column_formatters:
            return

        # Store columns that had formatters
        columns = list(self._column_formatters.keys())

        # Clear dictionary
        self._column_formatters.clear()

        # Emit dataChanged for each affected column
        if self.sourceModel() is not None:
            row_count = self.rowCount()
            if row_count > 0:
                for column in columns:
                    top_left = self.index(0, column)
                    bottom_right = self.index(row_count - 1, column)
                    self.dataChanged.emit(
                        top_left, bottom_right, [Qt.ItemDataRole.DisplayRole]
                    )
