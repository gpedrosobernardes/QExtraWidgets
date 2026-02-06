import typing

from PySide6.QtCore import Qt, QRect, QAbstractItemModel, QModelIndex
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QTableView, QWidget

from qextrawidgets.gui.icons.theme_responsive_icon import QThemeResponsiveIcon
from qextrawidgets.gui.proxys import QMultiFilterProxy
from qextrawidgets.widgets.dialogs import QFilterPopup
from qextrawidgets.widgets.views.filter_header_view import QFilterHeaderView


class QFilterableTableView(QTableView):
    """A QTableView extension that provides Excel-style filtering and sorting on headers."""

    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        """Initializes the filterable table.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)

        self._proxy = QMultiFilterProxy()
        super().setModel(self._proxy)
        self._popups: typing.Dict[int, QFilterPopup] = {}

        header = QFilterHeaderView(Qt.Orientation.Horizontal, self)
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self._on_header_clicked)
        self.setHorizontalHeader(header)

        self.setModel(QStandardItemModel(self))

    # --- Public API ---

    def setModel(self, model: typing.Optional[QAbstractItemModel]) -> None:
        """Sets the source model for the table and initializes filters.

        Args:
            model (Optional[QAbstractItemModel]): The data model to display.
        """
        if model is None:
            return

        if self._proxy.sourceModel():
            self._disconnect_model_signals(self._proxy.sourceModel())

        self._proxy.setSourceModel(model)

        if model:
            self._connect_model_signals(model)

        self._refresh_popups()

    def model(self) -> QAbstractItemModel:
        """Returns the source model (not the proxy).

        Returns:
            QAbstractItemModel: The source model.
        """
        return self._proxy.sourceModel()

    # --- Popup Logic ---

    def _refresh_popups(self) -> None:
        """Clears and recreates filter popups for all columns."""
        self._proxy.reset()

        for popup in self._popups.values():
            popup.deleteLater()
        self._popups.clear()

        model = self.model()
        if not model:
            return

        for col in range(model.columnCount()):
            self._create_popup(col)

    def _create_popup(self, logical_index: int) -> None:
        """Creates a filter popup for a specific column.

        Args:
            logical_index (int): Column index.
        """
        if logical_index in self._popups:
            return

        popup = QFilterPopup(self._proxy, logical_index, self)

        popup.accepted.connect(lambda: self._apply_filter(logical_index))

        popup.orderChanged.connect(lambda col, order: self.sortByColumn(col, order))

        popup.clearRequested.connect(lambda: self._clear_filter(logical_index))

        self._popups[logical_index] = popup
        self._update_header_icon(logical_index)

    def _on_header_clicked(self, logical_index: int) -> None:
        """Handles header clicks to show the filter popup.

        Args:
            logical_index (int): Column index clicked.
        """
        if logical_index not in self._popups:
            return

        popup = self._popups[logical_index]

        # QFilterPopup now handles unique values internally via proxy.
        # We just need to show it.

        header = self.horizontalHeader()
        viewport_pos = header.sectionViewportPosition(logical_index)
        global_pos = self.mapToGlobal(QRect(viewport_pos, 0, 0, 0).topLeft())

        popup.move(global_pos.x(), global_pos.y() + header.height())
        popup.setClearEnabled(self._proxy.isColumnFiltered(logical_index))
        popup.exec()

    def _apply_filter(self, logical_index: int) -> None:
        """Applies the selected filter from the popup to the proxy model.

        Args:
            logical_index (int): Column index.
        """
        popup = self._popups.get(logical_index)
        if not popup:
            return

        if popup.isFiltering():
            filter_data = popup.getSelectedData()
            self._proxy.setFilter(logical_index, filter_data)

        self._update_header_icon(logical_index)

    def _clear_filter(self, logical_index: int) -> None:
        """Clears the filter for the specified column.

        Args:
            logical_index (int): Column index.
        """
        self._proxy.setFilter(logical_index, None)
        self._update_header_icon(logical_index)

    def _update_header_icon(self, logical_index: int) -> None:
        """Updates the header icon to reflect if a filter is active.

        Args:
            logical_index (int): Column index.
        """
        if logical_index not in self._popups:
            return

        # The icon reflects if there is an ACTIVE filter in the popup
        icon_name = (
            "fa6s.filter"
            if self._proxy.isColumnFiltered(logical_index)
            else "fa6s.angle-down"
        )
        icon = QThemeResponsiveIcon.fromAwesome(icon_name)

        # Use the proxy to set the header data. This works for QSqlTableModel and others
        # that might not support setting header icons directly or easily.
        self._proxy.setHeaderData(
            logical_index,
            Qt.Orientation.Horizontal,
            icon,
            Qt.ItemDataRole.DecorationRole,
        )

    # --- Smart Data Logic ---

    # --- Model Signals ---

    def _connect_model_signals(self, model: QAbstractItemModel) -> None:
        """Connects signals to react to model changes.

        Args:
            model (QAbstractItemModel): The model to connect to.
        """
        model.columnsInserted.connect(self._on_columns_inserted)
        model.columnsRemoved.connect(self._on_columns_removed)
        model.modelReset.connect(self._refresh_popups)

    def _disconnect_model_signals(self, model: QAbstractItemModel) -> None:
        """Disconnects signals from the model.

        Args:
            model (QAbstractItemModel): The model to disconnect from.
        """
        try:
            model.columnsInserted.disconnect(self._on_columns_inserted)
            model.columnsRemoved.disconnect(self._on_columns_removed)
            model.modelReset.disconnect(self._refresh_popups)
        except RuntimeError:
            pass

    def _on_columns_inserted(self, parent: QModelIndex, start: int, end: int) -> None:
        """Handles columns inserted in the model.

        Args:
            parent (QModelIndex): Parent index.
            start (int): Start index.
            end (int): End index.
        """
        for i in range(start, end + 1):
            self._create_popup(i)

    def _on_columns_removed(self, parent: QModelIndex, start: int, end: int) -> None:
        """Handles columns removed from the model.

        Args:
            parent (QModelIndex): Parent index.
            start (int): Start index.
            end (int): End index.
        """
        self._refresh_popups()
