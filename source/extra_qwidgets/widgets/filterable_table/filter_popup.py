from typing import Generator, Set

from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QVBoxLayout, QPushButton, QHBoxLayout, QDialog, QLineEdit, QListView, QFrame, QCheckBox, QToolButton, QSizePolicy
)
from PySide6.QtCore import Qt, QSortFilterProxyModel

from extra_qwidgets.icons import QThemeResponsiveIcon


class QFilterPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setSizeGripEnabled(True)

        self._setup_ui()
        self._setup_model()
        self._setup_connections()

    def _setup_ui(self):
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
    def _create_filter_button(text: str):
        tool_button = QToolButton()
        tool_button.setText(text)
        tool_button.setAutoRaise(True)
        # TextBesideIcon é bom, mas certifique-se que o ícone existe
        tool_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        # Preferred é melhor que Expanding para botões de ferramenta,
        # para não ficarem gigantes horizontalmente sem necessidade.
        tool_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        tool_button.setCursor(Qt.CursorShape.PointingHandCursor)
        return tool_button

    def _setup_model(self):
        self.model = QStandardItemModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)

        # Filtros e Ordenação
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterRole(Qt.ItemDataRole.DisplayRole)
        self.proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.sort(0, Qt.SortOrder.AscendingOrder)

        self.items_listview.setModel(self.proxy_model)

    def _setup_connections(self):
        self.search_field.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.accept)
        self.order_button.clicked.connect(self.accept)
        self.reverse_order_button.clicked.connect(self.accept)
        self.clear_filter_button.clicked.connect(self._on_clear_filter)

        self.check_all_box.clicked.connect(self._on_check_all_clicked)
        self.model.itemChanged.connect(self._update_select_all_state)

    def _on_clear_filter(self):
        self.search_field.clear()
        self._set_all_items_checked(True)
        self.check_all_box.setCheckState(Qt.CheckState.Checked)

    def _on_check_all_clicked(self):
        state = self.check_all_box.checkState()
        is_checked = state == Qt.CheckState.Checked

        self.model.blockSignals(True)
        # Ao clicar em "Select All", afetamos apenas o que está VISÍVEL na busca
        rowCount = self.proxy_model.rowCount()
        for row in range(rowCount):
            proxy_idx = self.proxy_model.index(row, 0)
            source_idx = self.proxy_model.mapToSource(proxy_idx)
            item = self.model.itemFromIndex(source_idx)
            if item:
                item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
        self.model.blockSignals(False)
        self.check_all_box.setCheckState(state)

    def _update_select_all_state(self, item=None):
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

    def _set_all_items_checked(self, checked: bool):
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            item.setCheckState(state)

    # --- API de Dados ---

    def getSelectedData(self) -> Set[str]:
        """
        Retorna TODOS os itens marcados no modelo original,
        independente se estão filtrados pela busca do popup ou não.
        """
        data = set()
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item.checkState() == Qt.CheckState.Checked:
                data.add(item.text())
        return data

    def getData(self) -> Set[str]:
        """Retorna todos os dados contidos no popup."""
        return {self.model.item(row, 0).text() for row in range(self.model.rowCount())}

    def addData(self, data: str):
        if not self.model.findItems(data):
            item = QStandardItem(data)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Checked)
            self.model.appendRow(item)

    def removeData(self, data: str):
        """Remove o item do popup (usado quando ele não é mais válido no contexto)."""
        items = self.model.findItems(data)
        for item in items:
            self.model.removeRow(item.row())

    def isFiltering(self) -> bool:
        """
        Retorna True se existe algum item desmarcado.
        """
        for row in range(self.model.rowCount()):
            if self.model.item(row, 0).checkState() == Qt.CheckState.Unchecked:
                return True
        return False