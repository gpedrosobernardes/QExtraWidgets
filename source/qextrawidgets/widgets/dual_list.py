from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QListWidget, QAbstractItemView, QPushButton, QLineEdit, QLabel, QGroupBox, \
    QVBoxLayout, QHBoxLayout
from typing import List

from qextrawidgets.icons import QThemeResponsiveIcon


class QDualList(QWidget):
    """
    Base class containing layout structure and business logic.
    Instantiates widgets via factory methods (_create_*) to allow
    visual customization in child classes.
    """
    # Public signal
    selectionChanged = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- 1. Interface Construction (Directly in __init__) ---

        main_layout = QHBoxLayout(self)

        # A. Left Side (Available)
        # Creates the container using the factory method
        self._available_container = self._create_container(self.tr("Available"))
        # The container layout depends on the returned container type
        container_layout_l = QVBoxLayout(
            self._available_container) if not self._available_container.layout() else self._available_container.layout()

        self._search_input = self._create_search_input()
        self._list_available = self._create_list_widget()

        container_layout_l.addWidget(self._search_input)
        container_layout_l.addWidget(self._list_available)

        # B. Center (Buttons)
        buttons_layout = QVBoxLayout()
        buttons_layout.addStretch()

        self._btn_move_all_right = self._create_button(QThemeResponsiveIcon.fromAwesome("fa6s.angles-right"))
        self._btn_move_right = self._create_button(QThemeResponsiveIcon.fromAwesome("fa6s.angle-right"))
        self._btn_move_left = self._create_button(QThemeResponsiveIcon.fromAwesome("fa6s.angle-left"))
        self._btn_move_all_left = self._create_button(QThemeResponsiveIcon.fromAwesome("fa6s.angles-left"))

        buttons_layout.addWidget(self._btn_move_all_right)
        buttons_layout.addWidget(self._btn_move_right)
        buttons_layout.addWidget(self._btn_move_left)
        buttons_layout.addWidget(self._btn_move_all_left)
        buttons_layout.addStretch()

        # C. Right Side (Selected)
        self._selected_container = self._create_container(self.tr("Selected"))
        container_layout_r = QVBoxLayout(
            self._selected_container) if not self._selected_container.layout() else self._selected_container.layout()

        self._list_selected = self._create_list_widget()
        self._lbl_count = self._create_label(self.tr("0 items"))

        container_layout_r.addWidget(self._list_selected)
        container_layout_r.addWidget(self._lbl_count)

        # D. Final Composition
        main_layout.addWidget(self._available_container)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self._selected_container)

        # --- 2. Connections Setup ---
        self._setup_connections()

    # --- Factory Methods (Extension points for child class) ---

    def _create_container(self, title: str) -> QWidget:
        """Creates the default container (QGroupBox)."""
        box = QGroupBox(title)
        return box

    def _create_list_widget(self) -> QListWidget:
        """Creates the default list (QListWidget)."""
        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        list_widget.setDragEnabled(True)
        list_widget.setAcceptDrops(True)
        list_widget.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        list_widget.setAlternatingRowColors(True)
        return list_widget

    def _create_button(self, icon: QIcon) -> QPushButton:
        """Creates a default button."""
        btn = QPushButton()
        btn.setIcon(icon)
        return btn

    def _create_search_input(self) -> QLineEdit:
        """Creates a default input."""
        line = QLineEdit()
        line.setPlaceholderText(self.tr("Filter..."))
        return line

    def _create_label(self, text: str) -> QLabel:
        """Creates a default label."""
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        return lbl

    # --- Internal Logic (snake_case) ---

    def _setup_connections(self):
        # Buttons
        self._btn_move_right.clicked.connect(lambda: self._move_items(self._list_available, self._list_selected))
        self._btn_move_left.clicked.connect(lambda: self._move_items(self._list_selected, self._list_available))
        self._btn_move_all_right.clicked.connect(
            lambda: self._move_all_items(self._list_available, self._list_selected))
        self._btn_move_all_left.clicked.connect(lambda: self._move_all_items(self._list_selected, self._list_available))

        # Double Click
        self._list_available.itemDoubleClicked.connect(
            lambda: self._move_items(self._list_available, self._list_selected))
        self._list_selected.itemDoubleClicked.connect(
            lambda: self._move_items(self._list_selected, self._list_available))

        # Filter
        self._search_input.textChanged.connect(self._filter_available_items)

        # Monitoring
        self._list_selected.model().rowsInserted.connect(self._update_internal_count)
        self._list_selected.model().rowsRemoved.connect(self._update_internal_count)

    def _move_items(self, source_list, dest_list):
        items = source_list.selectedItems()
        for item in items:
            source_list.takeItem(source_list.row(item))
            dest_list.addItem(item)
        dest_list.sortItems()
        self._update_internal_count()

    def _move_all_items(self, source_list, dest_list):
        for i in range(source_list.count() - 1, -1, -1):
            item = source_list.item(i)
            if not item.isHidden():
                source_list.takeItem(i)
                dest_list.addItem(item)
        dest_list.sortItems()
        self._update_internal_count()

    def _filter_available_items(self, text: str):
        count = self._list_available.count()
        for i in range(count):
            item = self._list_available.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def _update_internal_count(self, parent=None, start=0, end=0):
        count = self._list_selected.count()
        self._lbl_count.setText(self.tr("{} items").format(count))
        current_data = [self._list_selected.item(i).text() for i in range(count)]
        self.selectionChanged.emit(current_data)

    # --- Public API (camelCase) ---

    def setAvailableItems(self, items: List[str]):
        self._list_available.clear()
        self._list_selected.clear()
        self._list_available.addItems(items)
        self._list_available.sortItems()
        self._update_internal_count()

    def getSelectedItems(self) -> List[str]:
        return [self._list_selected.item(i).text() for i in range(self._list_selected.count())]

    def setSelectedItems(self, items: List[str]):
        self._list_selected.clear()
        self._list_selected.addItems(items)
        self._update_internal_count()
