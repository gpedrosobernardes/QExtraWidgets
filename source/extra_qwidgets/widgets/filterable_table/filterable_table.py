import qtawesome
from PySide6.QtWidgets import (
    QTableWidgetItem, QTableView, QApplication
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QStandardItemModel, QStandardItem

from extra_qwidgets.utils import colorize_icon_by_theme
from extra_qwidgets.widgets.filterable_table.custom_header import CustomHeader
from extra_qwidgets.widgets.filterable_table.filter_popup import QFilterPopup
from extra_qwidgets.proxys.multi_filter_proxy import QMultiFilterProxy


# https://doc.qt.io/


class QFilterableTable(QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = QStandardItemModel()
        header = CustomHeader(Qt.Orientation.Horizontal, self)
        self.setHorizontalHeader(header)
        self._proxy = QMultiFilterProxy()
        self._proxy.setSourceModel(self._model)
        self._popups: list[QFilterPopup] = []
        self.setModel(self._proxy)
        self._setup_binds()

    def model(self) -> QStandardItemModel:
        return self._model

    def _add_popup(self, column: int):
        item = self._model.horizontalHeaderItem(column)
        if not item:
            item = QStandardItem()
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setText(str(column))
            self._model.setHorizontalHeaderItem(column, item)

        self._popups.append(self._new_popup(column))
        self._update_popup_icon(column)
        header = self.horizontalHeader()
        header.sectionClicked.connect(self._show_filter_popup)

    def _new_popup(self, column: int) -> QFilterPopup:
        popup = QFilterPopup()
        popup.apply_button.clicked.connect(lambda: self._filter_column(column))
        popup.order_button.clicked.connect(lambda: self.sortByColumn(column, Qt.SortOrder.AscendingOrder))
        popup.reverse_order_button.clicked.connect(lambda: self.sortByColumn(column, Qt.SortOrder.DescendingOrder))
        popup.apply_button.clicked.connect(lambda: self._update_popup_icon(column))
        return popup

    def _update_popup_icon(self, column: int):
        popup = self._popups[column]
        item = self._model.horizontalHeaderItem(column)
        if popup.isFiltering():
            item.setIcon(colorize_icon_by_theme(qtawesome.icon("fa6s.filter")))
        else:
            item.setIcon(colorize_icon_by_theme(qtawesome.icon("fa6s.angle-down")))

    def _show_filter_popup(self, index: int):
        popup = self._popups[index]
        pos = self.mapToGlobal(
            QRect(self.columnViewportPosition(index), 10, 0, 0).topLeft()
        )
        popup.move(pos.x(), pos.y() + self.horizontalHeader().height())
        popup.exec()

    def _filter_column(self, column: int):
        popup = self._popups[column]
        filter_data = popup.getSelectedVisibleData()
        self._proxy.setFilter(column, filter_data)

    def _on_theme_change(self):
        for column in range(self._model.columnCount()):
            self._update_popup_icon(column)

    def _setup_binds(self):
        self._model.itemChanged.connect(self._update_popup_items_by_item)
        self._model.columnsInserted.connect(self._on_columns_inserted)
        self._model.columnsRemoved.connect(self._on_columns_removed)
        QApplication.styleHints().colorSchemeChanged.connect(self._on_theme_change)

    def _on_columns_inserted(self, _: QStandardItemModel, start: int, end: int):
        for i in range(start, end + 1):
            self._add_popup(i)

    def _on_columns_removed(self, _: QStandardItemModel, start: int, end: int):
        for i in range(start, end + 1):
            self._popups[i].hide()
            self._popups.pop(i)

    def _update_popup_items_by_item(self, item: QTableWidgetItem):
        popup = self._popups[item.column()]
        popup_col_data = popup.getData()
        table_col_data = self._get_column_data(item.column())
        for i in table_col_data - popup_col_data:
            popup.addData(i)
        for i in popup_col_data - table_col_data:
            popup.removeData(i)

    def _get_column_data(self, col: int, limit: int = 1000) -> set[str]:
        return set(
            item.data(Qt.ItemDataRole.DisplayRole) for row in range(min(self._model.rowCount(), limit))
            if (item := self._model.item(row, col))
        )