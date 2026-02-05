from typing import Set

from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QVBoxLayout, QPushButton, QHBoxLayout, QDialog, QLineEdit, QListView, QFrame, QCheckBox, QToolButton, QSizePolicy,
    QWidget
)

from qextrawidgets.gui.icons import QThemeResponsiveIcon


class QFilterPopup(QDialog):
    """A popup dialog used for filtering and sorting columns in a QFilterableTable.

    Provides options to sort data, search for specific values, and select/deselect
    items to be displayed in the table.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """Initializes the filter popup.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setSizeGripEnabled(True)

        self._setup_ui()
        self._setup_model()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """Sets up the user interface components."""
        self.order_button = self._create_filter_button(self.tr("Order A to Z"))
        self.order_button.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.arrow-down-a-z"))

        self.reverse_order_button = self._create_filter_button(self.tr("Order Z to A"))
        self.reverse_order_button.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.arrow-down-z-a"))

        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.clear_filter_button = self._create_filter_button(self.tr("Clear filter"))
        self.clear_filter_button.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.filter-circle-xmark"))

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText(self.tr("Search..."))
        self.search_field.setClearButtonEnabled(True)

        self.check_all_box = QCheckBox(self.tr("(Select All)"))
        self.check_all_box.setTristate(True)
        self.check_all_box.setCheckState(Qt.CheckState.Checked)

        self.items_listview = QListView()
        self.items_listview.setUniformItemSizes(True)

        self.apply_button = QPushButton(self.tr("Apply"))
        self.cancel_button = QPushButton(self.tr("Cancel"))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addWidget(self.order_button)
        layout.addWidget(self.reverse_order_button)
        layout.addWidget(self.line)
        layout.addWidget(self.clear_filter_button)
        layout.addWidget(self.search_field)
        layout.addWidget(self.check_all_box)
        layout.addWidget(self.items_listview)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.apply_button)
        btn_layout.addWidget(self.cancel_button)
        layout.addLayout(btn_layout)

    @staticmethod
    def _create_filter_button(text: str) -> QToolButton:
        """Creates a tool button for filter actions.

        Args:
            text (str): Button text.

        Returns:
            QToolButton: The created tool button.
        """
        tool_button = QToolButton()
        tool_button.setText(text)
        tool_button.setAutoRaise(True)
        tool_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        tool_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        tool_button.setCursor(Qt.CursorShape.PointingHandCursor)
        return tool_button

    def _setup_model(self) -> None:
        """Sets up the data model and proxy model for the list view."""
        self.model = QStandardItemModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)

        # Filters and Sorting
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterRole(Qt.ItemDataRole.DisplayRole)
        self.proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.sort(0, Qt.SortOrder.AscendingOrder)

        self.items_listview.setModel(self.proxy_model)

    def _setup_connections(self) -> None:
        """Sets up signals and slots connections."""
        self.search_field.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.accept)
        self.order_button.clicked.connect(self.accept)
        self.reverse_order_button.clicked.connect(self.accept)
        self.clear_filter_button.clicked.connect(self._on_clear_filter)

        self.check_all_box.clicked.connect(self._on_check_all_clicked)
        self.model.itemChanged.connect(self._update_select_all_state)

    def _on_clear_filter(self) -> None:
        """Handles the clear filter action."""
        self.search_field.clear()
        self._set_all_items_checked(True)
        self.check_all_box.setCheckState(Qt.CheckState.Checked)

    def _on_check_all_clicked(self) -> None:
        """Handles clicking the 'Select All' checkbox."""
        state = self.check_all_box.checkState()
        is_checked = state == Qt.CheckState.Checked

        self.model.blockSignals(True)
        # When clicking "Select All", we only affect what is VISIBLE in the search
        row_count = self.proxy_model.rowCount()
        for row in range(row_count):
            proxy_idx = self.proxy_model.index(row, 0)
            source_idx = self.proxy_model.mapToSource(proxy_idx)
            item = self.model.itemFromIndex(source_idx)
            if item:
                item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
        self.model.blockSignals(False)
        self.check_all_box.setCheckState(state)

    def _update_select_all_state(self, item: QStandardItem = None) -> None:
        """Updates the state of the 'Select All' checkbox based on items.

        Args:
            item (QStandardItem, optional): The item that changed. Defaults to None.
        """
        checked_count = 0
        total_count = self.proxy_model.rowCount()

        if total_count == 0:
            return

        for row in range(total_count):
            proxy_idx = self.proxy_model.index(row, 0)
            source_idx = self.proxy_model.mapToSource(proxy_idx)
            item = self.model.itemFromIndex(source_idx)
            if item and item.checkState() == Qt.CheckState.Checked:
                checked_count += 1

        self.check_all_box.blockSignals(True)
        if checked_count == 0:
            self.check_all_box.setCheckState(Qt.CheckState.Unchecked)
        elif checked_count == total_count:
            self.check_all_box.setCheckState(Qt.CheckState.Checked)
        else:
            self.check_all_box.setCheckState(Qt.CheckState.PartiallyChecked)
        self.check_all_box.blockSignals(False)

    def _set_all_items_checked(self, checked: bool) -> None:
        """Sets the check state of all items in the model.

        Args:
            checked (bool): True to check all items, False to uncheck all.
        """
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            item.setCheckState(state)

    # --- Data API ---

    def getSelectedData(self) -> Set[str]:
        """Returns all checked items in the original model.

        Regardless of whether they are filtered by the popup search or not.

        Returns:
            Set[str]: Set of checked item texts.
        """
        data = set()
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item.checkState() == Qt.CheckState.Checked:
                data.add(item.text())
        return data

    def getData(self) -> Set[str]:
        """Returns all data contained in the popup.

        Returns:
            Set[str]: Set of all item texts.
        """
        return {self.model.item(row, 0).text() for row in range(self.model.rowCount())}

    def addData(self, data: str) -> None:
        """Adds a new item to the filter popup if it doesn't exist.

        Args:
            data (str): Item text to add.
        """
        if not self.model.findItems(data):
            item = QStandardItem(data)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Checked)
            self.model.appendRow(item)

    def removeData(self, data: str) -> None:
        """Removes the item from the popup.

        Args:
            data (str): Item text to remove.
        """
        items = self.model.findItems(data)
        for item in items:
            self.model.removeRow(item.row())

    def isFiltering(self) -> bool:
        """Checks if there is any unchecked item, indicating an active filter.

        Returns:
            bool: True if any item is unchecked, False otherwise.
        """
        for row in range(self.model.rowCount()):
            if self.model.item(row, 0).checkState() == Qt.CheckState.Unchecked:
                return True
        return False
