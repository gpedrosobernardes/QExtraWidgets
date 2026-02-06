import typing

from PySide6.QtCore import Qt, QSortFilterProxyModel, QAbstractItemModel, Slot
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QDialog,
    QLineEdit,
    QListView,
    QFrame,
    QCheckBox,
    QToolButton,
    QSizePolicy,
    QWidget,
)

from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.gui.proxys import (
    QCheckStateProxyModel,
    QUniqueValuesProxyModel,
)


class QFilterPopup(QDialog):
    """A popup dialog used for filtering and sorting columns in a QFilterableTable.

    Provides options to sort data, search for specific values, and select/deselect
    items to be displayed in the table.
    """

    orderChanged = Signal(int, Qt.SortOrder)
    clearRequested = Signal()

    def __init__(
        self,
        model: QAbstractItemModel,
        column: int,
        parent: typing.Optional[QWidget] = None,
    ) -> None:
        """Initializes the filter popup.

        Args:
            model (QAbstractItemModel): The source data model.
            column (int): The column to filter.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setSizeGripEnabled(True)

        self._order_button = self._create_filter_button(self.tr("Order A to Z"))
        self._order_button.setIcon(
            QThemeResponsiveIcon.fromAwesome("fa6s.arrow-down-a-z")
        )

        self._reverse_orden_button = self._create_filter_button(self.tr("Order Z to A"))
        self._reverse_orden_button.setIcon(
            QThemeResponsiveIcon.fromAwesome("fa6s.arrow-down-z-a")
        )

        self._clear_filter_button = self._create_filter_button(self.tr("Clear Filter"))
        self._clear_filter_button.setIcon(
            QThemeResponsiveIcon.fromAwesome("fa6s.filter-circle-xmark")
        )

        self._line = QFrame()
        self._line.setFrameShape(QFrame.Shape.HLine)
        self._line.setFrameShadow(QFrame.Shadow.Sunken)

        self._search_field = QLineEdit()
        self._search_field.setPlaceholderText(self.tr("Search..."))
        self._search_field.setClearButtonEnabled(True)

        self._check_all_box = QCheckBox(self.tr("(Select All)"))
        self._check_all_box.setTristate(True)
        self._check_all_box.setCheckState(Qt.CheckState.Checked)

        self._list_view = QListView()
        self._list_view.setUniformItemSizes(True)

        self._apply_button = QPushButton(self.tr("Apply"))
        self._cancel_button = QPushButton(self.tr("Cancel"))

        self._setup_layout()
        self._setup_model(model, column)
        self._setup_connections()

    def _setup_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addWidget(self._order_button)
        layout.addWidget(self._reverse_orden_button)
        layout.addWidget(self._clear_filter_button)
        layout.addWidget(self._line)

        layout.addWidget(self._search_field)
        layout.addWidget(self._check_all_box)
        layout.addWidget(self._list_view)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self._apply_button)
        btn_layout.addWidget(self._cancel_button)
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
        tool_button.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        tool_button.setCursor(Qt.CursorShape.PointingHandCursor)
        return tool_button

    def _setup_model(self, model: QAbstractItemModel, column: int) -> None:
        """Sets up the data model and proxy chain for the list view."""
        # 1. Unique Values Proxy (Filters source to show only unique rows for the column)
        self._unique_proxy = QUniqueValuesProxyModel(self)
        self._unique_proxy.setSourceModel(model)
        self._unique_proxy.setTargetColumn(column)

        # 2. Check State Proxy (Adds checkbox state to the unique rows)
        self._check_proxy = QCheckStateProxyModel(self)
        self._check_proxy.setSourceModel(self._unique_proxy)
        self._check_proxy.setInitialCheckState(Qt.CheckState.Checked)

        # 3. Sort Proxy (Allows searching/sorting within the popup)
        self._proxy_model = QSortFilterProxyModel(self)
        self._proxy_model.setSourceModel(self._check_proxy)
        self._proxy_model.setFilterKeyColumn(column)

        # Filters and Sorting settings
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy_model.setFilterRole(Qt.ItemDataRole.DisplayRole)
        self._proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy_model.setDynamicSortFilter(True)
        self._proxy_model.sort(column, Qt.SortOrder.AscendingOrder)

        self._list_view.setModel(self._proxy_model)
        # Ensure we show the correct column in the list view (as it's a table model potentially)
        self._list_view.setModelColumn(column)

    def _setup_connections(self) -> None:
        """Sets up signals and slots connections."""
        self._search_field.textChanged.connect(self._proxy_model.setFilterFixedString)
        self._cancel_button.clicked.connect(self.reject)
        self._order_button.clicked.connect(self.reject)
        self._reverse_orden_button.clicked.connect(self.reject)
        self._clear_filter_button.clicked.connect(self._on_clear_clicked)
        self._apply_button.clicked.connect(self.accept)

        self._check_all_box.clicked.connect(self._on_check_all_clicked)
        self._proxy_model.dataChanged.connect(self._update_select_all_state)

        self._order_button.clicked.connect(
            lambda: self.orderChanged.emit(
                self._proxy_model.filterKeyColumn(), Qt.SortOrder.AscendingOrder
            )
        )
        self._reverse_orden_button.clicked.connect(
            lambda: self.orderChanged.emit(
                self._proxy_model.filterKeyColumn(), Qt.SortOrder.DescendingOrder
            )
        )

    def _on_check_all_clicked(self) -> None:
        """Handles clicking the 'Select All' checkbox."""
        state = self._check_all_box.checkState()

        # When clicking "Select All", we only affect what is VISIBLE in the search
        # We need to iterate over visible rows in the SortProxy
        row_count = self._proxy_model.rowCount()
        column = self._proxy_model.filterKeyColumn()  # Should be our target column

        for row in range(row_count):
            # Map from sort proxy to check proxy
            sort_index = self._proxy_model.index(row, column)
            check_index = self._proxy_model.mapToSource(sort_index)

            if check_index.isValid():
                self._check_proxy.setData(
                    check_index, state, Qt.ItemDataRole.CheckStateRole
                )

        self._check_all_box.setCheckState(state)

    @Slot()
    def _update_select_all_state(self) -> None:
        """Updates the state of the 'Select All' checkbox based on items.

        """
        checked_count = 0
        total_count = self._proxy_model.rowCount()

        if total_count == 0:
            return

        for row in range(total_count):
            column = self._proxy_model.filterKeyColumn()
            proxy_idx = self._proxy_model.index(row, column)
            check_state = self._proxy_model.data(
                proxy_idx, Qt.ItemDataRole.CheckStateRole
            )

            if not isinstance(check_state, Qt.CheckState):
                check_state = Qt.CheckState(check_state)

            if check_state == Qt.CheckState.Checked:
                checked_count += 1

        self._check_all_box.blockSignals(True)
        if checked_count == 0:
            self._check_all_box.setCheckState(Qt.CheckState.Unchecked)
        elif checked_count == total_count:
            self._check_all_box.setCheckState(Qt.CheckState.Checked)
        else:
            self._check_all_box.setCheckState(Qt.CheckState.PartiallyChecked)
        self._check_all_box.blockSignals(False)

    def _on_clear_clicked(self) -> None:
        """Handles the clear filter button click."""
        self._search_field.clear()
        self.clearRequested.emit()
        self.reject()

    def setClearEnabled(self, enabled: bool) -> None:
        """Sets the enabled state of the clear filter button.

        Args:
            enabled (bool): True to enable, False to disable.
        """
        self._clear_filter_button.setEnabled(enabled)

    # --- Data API ---

    def accept(self) -> None:
        super().accept()
        self._update_select_all_state()

    def getSelectedData(self) -> typing.Set[str]:
        """Returns all checked items in the unique check proxy that are visible in the proxy model.

        Returns:
            Set[str]: Set of checked item texts.
        """
        data = set()
        # Iterate over the proxy model (which contains visible values)
        row_count = self._proxy_model.rowCount()
        column = self._proxy_model.filterKeyColumn()

        for row in range(row_count):
            index = self._proxy_model.index(row, column)

            if (
                self._proxy_model.data(index, Qt.ItemDataRole.CheckStateRole)
                == Qt.CheckState.Checked
            ):
                val = self._proxy_model.data(index, Qt.ItemDataRole.DisplayRole)
                data.add(str(val))
        return data

    def isFiltering(self) -> bool:
        """Checks if there is any unchecked item, indicating an active filter.

        Returns:
            bool: True if any item is unchecked, False otherwise.
        """
        return bool(self._unique_proxy.rowCount() - len(self.getSelectedData()))
