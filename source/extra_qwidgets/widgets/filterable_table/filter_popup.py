from typing import Generator

from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QVBoxLayout, QPushButton, QHBoxLayout, QDialog, QLineEdit, QListView, QFrame
)
from PySide6.QtCore import Qt, QSortFilterProxyModel
import qtawesome

from extra_qwidgets.widgets.filterable_table.filter_tool_button import QFilterToolButton


class QFilterPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setSizeGripEnabled(True)
        self.order_button = QFilterToolButton()
        self.order_button.setText(self.tr("Order by A to Z"))
        self.order_button.setIcon(qtawesome.icon("fa6s.arrow-down-a-z"))
        self.reverse_order_button = QFilterToolButton()
        self.reverse_order_button.setText(self.tr("Order by Z to A "))
        self.reverse_order_button.setIcon(qtawesome.icon("fa6s.arrow-down-z-a"))
        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.clear_filter_button = QFilterToolButton()
        self.clear_filter_button.setText(self.tr("Clear filter"))
        self.clear_filter_button.setIcon(qtawesome.icon("fa6s.filter-circle-xmark"))
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText(self.tr("Search"))
        self.model = QStandardItemModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.items_listview = QListView()
        self.items_listview.setModel(self.proxy_model)
        self.apply_button = QPushButton(self.tr("Apply"))
        self.apply_button.clicked.connect(self._on_apply_button)
        self.cancel_button = QPushButton(self.tr("Cancel"))
        self._setup_binds()
        self._setup_layout()

    def _setup_binds(self):
        self.search_field.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.cancel_button.clicked.connect(self.hide)
        self.apply_button.clicked.connect(self.hide)
        self.order_button.clicked.connect(self.hide)
        self.reverse_order_button.clicked.connect(self.hide)
        self.clear_filter_button.clicked.connect(self._on_clear_filter)

    def _on_clear_filter(self):
        self.search_field.setText("")
        self.check_all()

    def _setup_layout(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.order_button)
        layout.addWidget(self.reverse_order_button)
        layout.addWidget(self.line)
        layout.addWidget(self.clear_filter_button)
        layout.addWidget(self.search_field)
        layout.addWidget(self.items_listview)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)

    def get_selected_visible_data(self) -> set[str]:
        return {item.data(Qt.ItemDataRole.DisplayRole) for row in range(self.proxy_model.rowCount())
                if (item := self.model.itemFromIndex(self.proxy_model.mapToSource(self.proxy_model.index(row, 0))))
                .checkState() == Qt.CheckState.Checked}

    def get_data(self) -> set[str]:
        return set(item.data(Qt.ItemDataRole.DisplayRole) for item in self.get_items())

    def _on_apply_button(self):
        if self.search_field.text():
            self._check_all_visible_items()

    def _check_all_visible_items(self):
        for item in self.get_items():
            proxy_index = self.proxy_model.mapFromSource(item.index())
            item.setCheckState(Qt.CheckState.Checked if proxy_index.isValid() else Qt.CheckState.Unchecked)

    def check_all(self):
        for item in self.get_items():
            item.setCheckState(Qt.CheckState.Checked)

    def get_items(self) -> Generator[QStandardItem]:
        for row in range(self.model.rowCount()):
            yield self.model.item(row, 0)

    def is_filtering(self):
        return any(map(lambda i: i.checkState() == Qt.CheckState.Unchecked, self.get_items()))

    def add_data(self, data: str):
        item = QStandardItem(data)
        item.setCheckable(True)
        item.setCheckState(Qt.CheckState.Checked)
        self.model.appendRow(item)

    def remove_data(self, data: str):
        items = self.model.findItems(data)
        for i in items:
            self.model.removeRow(i.row())
