import qtawesome
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QListWidget, QAbstractItemView, QPushButton, QLineEdit, QLabel, QGroupBox, \
    QVBoxLayout, QHBoxLayout

from extra_qwidgets.icons import QThemeResponsiveIcon


class QDualList(QWidget):
    """
    Classe base que contém a estrutura do layout e a lógica de negócios.
    Instancia os widgets através de métodos fábrica (_create_*) para permitir
    customização visual nas classes filhas.
    """
    # Sinal público
    selectionChanged = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- 1. Construção da Interface (Direto no __init__) ---

        main_layout = QHBoxLayout(self)

        # A. Lado Esquerdo (Disponíveis)
        # Cria o container usando o método fábrica
        self._available_container = self._create_container("Disponíveis")
        # O layout do container depende do tipo de container retornado
        container_layout_l = QVBoxLayout(
            self._available_container) if not self._available_container.layout() else self._available_container.layout()

        self._search_input = self._create_search_input()
        self._list_available = self._create_list_widget()

        container_layout_l.addWidget(self._search_input)
        container_layout_l.addWidget(self._list_available)

        # B. Centro (Botões)
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

        # C. Lado Direito (Selecionados)
        self._selected_container = self._create_container("Selecionados")
        container_layout_r = QVBoxLayout(
            self._selected_container) if not self._selected_container.layout() else self._selected_container.layout()

        self._list_selected = self._create_list_widget()
        self._lbl_count = self._create_label("0 itens")

        container_layout_r.addWidget(self._list_selected)
        container_layout_r.addWidget(self._lbl_count)

        # D. Composição Final
        main_layout.addWidget(self._available_container)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self._selected_container)

        # --- 2. Configuração das Conexões ---
        self._setup_connections()

    # --- Factory Methods (Pontos de extensão para a classe filha) ---

    @staticmethod
    def _create_container(title: str) -> QWidget:
        """Cria o container padrão (QGroupBox)."""
        box = QGroupBox(title)
        return box

    @staticmethod
    def _create_list_widget() -> QListWidget:
        """Cria a lista padrão (QListWidget)."""
        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        list_widget.setDragEnabled(True)
        list_widget.setAcceptDrops(True)
        list_widget.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        list_widget.setAlternatingRowColors(True)
        return list_widget

    @staticmethod
    def _create_button(icon: QIcon) -> QPushButton:
        """Cria um botão padrão."""
        btn = QPushButton()
        btn.setIcon(icon)
        return btn

    @staticmethod
    def _create_search_input() -> QLineEdit:
        """Cria um input padrão."""
        line = QLineEdit()
        line.setPlaceholderText("Filtrar...")
        return line

    @staticmethod
    def _create_label(text: str) -> QLabel:
        """Cria um label padrão."""
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        return lbl

    # --- Lógica Interna (snake_case) ---

    def _setup_connections(self):
        # Botões
        self._btn_move_right.clicked.connect(lambda: self._move_items(self._list_available, self._list_selected))
        self._btn_move_left.clicked.connect(lambda: self._move_items(self._list_selected, self._list_available))
        self._btn_move_all_right.clicked.connect(
            lambda: self._move_all_items(self._list_available, self._list_selected))
        self._btn_move_all_left.clicked.connect(lambda: self._move_all_items(self._list_selected, self._list_available))

        # Duplo Clique
        self._list_available.itemDoubleClicked.connect(
            lambda: self._move_items(self._list_available, self._list_selected))
        self._list_selected.itemDoubleClicked.connect(
            lambda: self._move_items(self._list_selected, self._list_available))

        # Filtro
        self._search_input.textChanged.connect(self._filter_available_items)

        # Monitoramento
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
        self._lbl_count.setText(f"{count} itens")
        current_data = [self._list_selected.item(i).text() for i in range(count)]
        self.selectionChanged.emit(current_data)

    # --- API Pública (camelCase) ---

    def setAvailableItems(self, items: list[str]):
        self._list_available.clear()
        self._list_selected.clear()
        self._list_available.addItems(items)
        self._list_available.sortItems()
        self._update_internal_count()

    def getSelectedItems(self) -> list[str]:
        return [self._list_selected.item(i).text() for i in range(self._list_selected.count())]

    def setSelectedItems(self, items: list[str]):
        self._list_selected.clear()
        self._list_selected.addItems(items)
        self._update_internal_count()