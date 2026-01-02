from functools import partial

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton,
                               QButtonGroup, QSpinBox)

from extra_qwidgets.icons import QThemeResponsiveIcon


class QPager(QWidget):
    """
    Componente de paginação.
    - Janela deslizante de botões.
    - Clique na página atual para digitar o número (edição in-place).
    """

    # Sinais públicos
    currentPageChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Variáveis de Dados ---
        self._total_pages = 1
        self._current_page = 1
        self._max_visible_buttons = 5

        # --- Configuração de UI e Layout ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Grupo para exclusividade visual
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)

        # Lista para rastrear widgets dinâmicos
        self._page_widgets = []

        # 1. Botões de Navegação
        self._btn_first = self._create_nav_button(QThemeResponsiveIcon.fromAwesome("fa6s.backward-step"))
        self._btn_prev = self._create_nav_button(QThemeResponsiveIcon.fromAwesome("fa6s.angle-left"))
        self._btn_next = self._create_nav_button(QThemeResponsiveIcon.fromAwesome("fa6s.angle-right"))
        self._btn_last = self._create_nav_button(QThemeResponsiveIcon.fromAwesome("fa6s.forward-step"))

        # 2. Layout para os números (onde a mágica acontece)
        self._numbers_layout = QHBoxLayout()
        self._numbers_layout.setContentsMargins(0, 0, 0, 0)
        self._numbers_layout.setSpacing(2)

        # 3. Adiciona ao layout principal
        main_layout.addWidget(self._btn_first)
        main_layout.addWidget(self._btn_prev)
        main_layout.addLayout(self._numbers_layout)
        main_layout.addWidget(self._btn_next)
        main_layout.addWidget(self._btn_last)

        # --- Conexões ---
        self._setup_connections()

        # Inicialização
        self._update_view()

    # --- Métodos Internos de Criação ---

    @staticmethod
    def _create_nav_button(icon: QIcon) -> QPushButton:
        btn = QPushButton()
        btn.setIcon(icon)
        btn.setFixedSize(30, 30)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    @staticmethod
    def _create_page_button(text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setFixedSize(30, 30)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def _create_editor(self) -> QSpinBox:
        """Cria o input numérico que substitui o botão."""
        spin = QSpinBox()
        spin.setFixedSize(60, 30)  # Um pouco mais largo para caber números grandes
        spin.setFrame(False)  # Sem borda para parecer integrado
        spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)  # Remove setinhas cima/baixo
        spin.setRange(1, self._total_pages)
        spin.setValue(self._current_page)
        return spin

    def _setup_connections(self):
        self._btn_first.clicked.connect(lambda: self.setCurrentPage(1))
        self._btn_prev.clicked.connect(lambda: self.setCurrentPage(self._current_page - 1))
        self._btn_next.clicked.connect(lambda: self.setCurrentPage(self._current_page + 1))
        self._btn_last.clicked.connect(lambda: self.setCurrentPage(self._total_pages))

    # --- Lógica de Visualização e Edição ---

    def _update_view(self):
        """Reconstroi a barra de números."""

        # 1. Calcular Janela Deslizante
        half = self._max_visible_buttons // 2
        start_page = max(1, self._current_page - half)
        end_page = min(self._total_pages, start_page + self._max_visible_buttons - 1)

        if end_page - start_page + 1 < self._max_visible_buttons:
            start_page = max(1, end_page - self._max_visible_buttons + 1)

        # 2. Limpeza Total da área numérica
        while self._numbers_layout.count():
            item = self._numbers_layout.takeAt(0)
            widget = item.widget()
            if widget:
                if isinstance(widget, QPushButton):
                    self._button_group.removeButton(widget)
                widget.deleteLater()
        self._page_widgets.clear()

        # 3. Construção dos Botões
        for page_num in range(start_page, end_page + 1):
            btn = self._create_page_button(str(page_num))
            self._button_group.addButton(btn)

            if page_num == self._current_page:
                btn.setChecked(True)
                # O botão atual não apenas navega, ele abre a edição
                btn.setToolTip("Clique para digitar a página")
                btn.clicked.connect(partial(self.__on_edit_requested, btn))
            else:
                # Botões normais apenas navegam
                btn.clicked.connect(partial(self.setCurrentPage, page_num))

            self._numbers_layout.addWidget(btn)
            self._page_widgets.append(btn)

        # 4. Estados de Navegação
        self._btn_first.setEnabled(self._current_page > 1)
        self._btn_prev.setEnabled(self._current_page > 1)
        self._btn_next.setEnabled(self._current_page < self._total_pages)
        self._btn_last.setEnabled(self._current_page < self._total_pages)

    def __on_edit_requested(self, button_sender: QPushButton):
        """
        Slot chamado quando o usuário clica na página atual.
        Substitui o botão por um SpinBox.
        """
        # 1. Identificar posição no layout
        index = self._numbers_layout.indexOf(button_sender)
        if index == -1: return

        # 2. Criar e configurar o editor
        spin = self._create_editor()

        # 3. Substituir no layout (Swap)
        # Removemos o botão do layout e escondemos (não deletamos ainda para evitar crash em slots ativos)
        item = self._numbers_layout.takeAt(index)
        button_sender.hide()
        self._button_group.removeButton(button_sender)  # Importante para não bugar o grupo

        self._numbers_layout.insertWidget(index, spin)
        spin.setFocus()
        spin.selectAll()

        # 4. Conexões do Editor
        # Se apertar Enter ou perder o foco, confirma a edição
        spin.editingFinished.connect(lambda: self.setCurrentPage(spin.value()))

        # Se perder o foco sem apertar enter, forçamos o update para restaurar o botão
        # (Isso é feito implicitamente pois setCurrentPage chama _update_view)

    # --- API Pública ---

    def setTotalPages(self, total: int):
        if total < 1: total = 1
        self._total_pages = total
        if self._current_page > total:
            self.setCurrentPage(total)
        else:
            self._update_view()

    def totalPages(self):
        return self._total_pages

    def setVisibleButtonCount(self, count: int):
        if count < 1: count = 1
        self._max_visible_buttons = count
        self._update_view()

    def visibleButtonCount(self):
        return self._max_visible_buttons

    def setCurrentPage(self, page: int):
        if page < 1: page = 1
        if page > self._total_pages: page = self._total_pages

        # Atualiza o estado
        self._current_page = page

        # Emite sinal apenas se mudou
        # Mas SEMPRE chama _update_view para garantir que o SpinBox
        # (se existir) seja destruído e o botão volte.
        self._update_view()
        self.currentPageChanged.emit(page)

    def currentPage(self):
        return self._current_page