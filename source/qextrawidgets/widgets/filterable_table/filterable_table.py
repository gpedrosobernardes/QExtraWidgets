from typing import Dict, Set, Optional

from PySide6.QtCore import Qt, QRect, QAbstractItemModel
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QTableView, QWidget
)

from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.proxys.multi_filter import QMultiFilterProxy
from qextrawidgets.widgets.filterable_table.custom_header import CustomHeader
from qextrawidgets.widgets.filterable_table.filter_popup import QFilterPopup


class QFilterableTable(QTableView):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._proxy = QMultiFilterProxy()
        self._popups: Dict[int, QFilterPopup] = {}

        header = CustomHeader(Qt.Orientation.Horizontal, self)
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self._on_header_clicked)
        self.setHorizontalHeader(header)

        self.setModel(QStandardItemModel(self))

    # --- Public API ---

    def setModel(self, model: QAbstractItemModel):
        if self._proxy.sourceModel():
            self._disconnect_model_signals(self._proxy.sourceModel())

        self._proxy.setSourceModel(model)
        super().setModel(self._proxy)

        if model:
            self._connect_model_signals(model)
            self._refresh_popups()

    def model(self) -> QAbstractItemModel:
        return self._proxy.sourceModel()

    # --- Popup Logic ---

    def _refresh_popups(self):
        for popup in self._popups.values():
            popup.deleteLater()
        self._popups.clear()

        model = self.model()
        if not model:
            return

        for col in range(model.columnCount()):
            self._create_popup(col)

    def _create_popup(self, logical_index: int):
        if logical_index in self._popups:
            return

        popup = QFilterPopup(self)

        popup.apply_button.clicked.connect(lambda _, col=logical_index: self._apply_filter(col))
        popup.order_button.clicked.connect(
            lambda _, col=logical_index: self.sortByColumn(col, Qt.SortOrder.AscendingOrder))
        popup.reverse_order_button.clicked.connect(
            lambda _, col=logical_index: self.sortByColumn(col, Qt.SortOrder.DescendingOrder))

        self._popups[logical_index] = popup
        self._update_header_icon(logical_index)

    def _on_header_clicked(self, logical_index: int):
        if logical_index not in self._popups:
            return

        popup = self._popups[logical_index]

        # 1. Calculates which values are valid considering filters from OTHER columns
        visible_values = self._get_unique_column_values(logical_index)

        # 2. Synchronizes the Popup (Adds new and REMOVES invalid ones)
        current_data = popup.getData()

        # Adds what is missing
        for val in visible_values - current_data:
            popup.addData(val)

        # Removes what shouldn't be there (to avoid visual inconsistency)
        for val in current_data - visible_values:
            popup.removeData(val)

        header = self.horizontalHeader()
        viewport_pos = header.sectionViewportPosition(logical_index)
        global_pos = self.mapToGlobal(QRect(viewport_pos, 0, 0, 0).topLeft())

        popup.move(global_pos.x(), global_pos.y() + header.height())
        popup.exec()

    def _apply_filter(self, logical_index: int):
        popup = self._popups.get(logical_index)
        if not popup:
            return

        # Fix to avoid "lock" behavior:
        # If the popup is NOT filtering (i.e., all visible items in the popup are checked),
        # we remove the filter from the proxy (passing None).
        # This prevents items hidden by other columns from being locked out of the list
        # when other filters are cleared.
        if popup.isFiltering():
            filter_data = popup.getSelectedData()
            self._proxy.setFilter(logical_index, filter_data)
        else:
            self._proxy.setFilter(logical_index, None)

        self._update_header_icon(logical_index)

    def _update_header_icon(self, logical_index: int):
        if logical_index not in self._popups:
            return

        popup = self._popups[logical_index]
        model = self.model()

        if isinstance(model, QStandardItemModel):
            item = model.horizontalHeaderItem(logical_index)
            if not item:
                item = QStandardItem(str(logical_index))
                model.setHorizontalHeaderItem(logical_index, item)

            # The icon reflects if there is an ACTIVE filter in the popup
            icon_name = "fa6s.filter" if popup.isFiltering() else "fa6s.angle-down"
            item.setIcon(QThemeResponsiveIcon.fromAwesome(icon_name))

    # --- Smart Data Logic ---

    def _get_unique_column_values(self, target_col: int, limit: int = 5000) -> Set[str]:
        """
        Returns unique values from column `target_col`,
        CONSIDERING active filters in all OTHER columns.
        """
        model = self.model()
        values = set()

        # 1. Captures filter state from OTHER columns
        active_filters: Dict[int, Set[str]] = {}

        for col_idx, popup in self._popups.items():
            # Ignores current column to show all its options
            if col_idx == target_col:
                continue

            if popup.isFiltering():
                active_filters[col_idx] = popup.getSelectedData()

        # 2. Scans source model checking row validity
        rows_to_scan = min(model.rowCount(), limit)

        for row in range(rows_to_scan):
            row_is_visible = True

            if active_filters:
                for filter_col, allowed_values in active_filters.items():
                    idx = model.index(row, filter_col)
                    val = str(model.data(idx, Qt.ItemDataRole.DisplayRole))

                    if val not in allowed_values:
                        row_is_visible = False
                        break

            if row_is_visible:
                idx_target = model.index(row, target_col)
                data = model.data(idx_target, Qt.ItemDataRole.DisplayRole)
                if data is not None:
                    values.add(str(data))

        return values

    # --- Model Signals ---

    def _connect_model_signals(self, model: QAbstractItemModel):
        model.columnsInserted.connect(self._on_columns_inserted)
        model.columnsRemoved.connect(self._on_columns_removed)
        model.modelReset.connect(self._refresh_popups)

    def _disconnect_model_signals(self, model: QAbstractItemModel):
        try:
            model.columnsInserted.disconnect(self._on_columns_inserted)
            model.columnsRemoved.disconnect(self._on_columns_removed)
            model.modelReset.disconnect(self._refresh_popups)
        except RuntimeError:
            pass

    def _on_columns_inserted(self, parent, start: int, end: int):
        for i in range(start, end + 1):
            self._create_popup(i)

    def _on_columns_removed(self, parent, start: int, end: int):
        self._refresh_popups()
