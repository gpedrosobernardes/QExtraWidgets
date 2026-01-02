import typing
from enum import Enum

from PySide6.QtCore import QSize, Qt, Signal, QPoint, QEvent, QAbstractProxyModel
from PySide6.QtGui import QStandardItemModel, QStandardItem, QMouseEvent
from PySide6.QtWidgets import QListView, QAbstractScrollArea, QSizePolicy
from emojis.db import Emoji

from extra_qwidgets.proxys.emoji_sort_filter import EmojiSortFilterProxyModel
from extra_qwidgets.widgets.emoji_picker.emoji_delegate import EmojiDelegate


class QEmojiGrid(QListView):
    # Sinais
    mouseEnteredEmoji = Signal(Emoji, QStandardItem)  # object = Emoji
    mouseLeftEmoji = Signal(Emoji, QStandardItem)
    emojiClicked = Signal(Emoji, QStandardItem)
    contextMenu = Signal(Emoji, QStandardItem, QPoint)

    class LimitTreatment(int, Enum):
        RemoveFirstOne = 1
        RemoveLastOne = 2

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__model = QStandardItemModel(self)

        # Assumindo que você tem o Proxy importado ou definido
        self.__last_index = None
        self.__limit = float("inf")
        self.__limit_treatment = None
        self.__proxy = EmojiSortFilterProxyModel(self)
        self.__proxy.setSourceModel(self.__model)
        self.setModel(self.__proxy)

        self.setMouseTracking(True)  # Essencial para o hover funcionar
        self.setIconSize(QSize(36, 36))
        self.setGridSize(QSize(40, 40))

        # Configuração de performance
        self.setItemDelegate(EmojiDelegate(self))

        # Configurações padrão
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setUniformItemSizes(True)
        self.setWrapping(True)
        self.setDragEnabled(False)

        # Desliga as barras de rolagem (o pai deve rolar)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Política de tamanho: Expande horizontalmente, Fixo verticalmente (baseado no sizeHint)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)

        # Ajuste nativo (ajuda, mas o sizeHint faz o trabalho pesado)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

    def sizeHint(self) -> QSize:
        """
        Diz ao Layout pai qual o tamanho ideal deste widget.
        O Qt chama isso automaticamente quando o layout é invalidado.
        """
        if self.model() is None or self.model().rowCount() == 0:
            return QSize(0, 0)

        # Largura disponível (se o widget ainda não foi mostrado, usa um valor padrão)
        width = self.width() if self.width() > 0 else 400

        # Dimensões do grid
        grid_sz = self.gridSize()
        if grid_sz.isEmpty():
            grid_sz = QSize(40, 40)  # Fallback

        # Cálculo matemático
        item_width = grid_sz.width()
        item_height = grid_sz.height()

        # Quantos cabem por linha?
        items_per_row = max(1, width // item_width)

        # Quantas linhas precisamos?
        total_items = self.model().rowCount()
        rows = (total_items + items_per_row - 1) // items_per_row  # Ceil division

        height = rows * item_height + 5  # +5 padding de segurança

        return QSize(width, height)

    def resizeEvent(self, event):
        """
        Quando a largura muda, o número de linhas muda.
        Precisamos avisar o layout para ler o sizeHint() de novo.
        """
        super().resizeEvent(event)
        self.updateGeometry()

    # --- Eventos (snake_case padrão Python/Qt) ---

    def mouseMoveEvent(self, e: QMouseEvent):
        """Gerencia a detecção de entrada/saída do mouse nos itens."""
        super().mouseMoveEvent(e)

        index = self.indexAt(e.pos())

        # Se o mouse saiu de um item válido ou entrou no vazio
        if self.__last_index and (not index.isValid() or index != self.__last_index):
            item = self.__get_item_from_index(self.__last_index)
            if item:
                emoji = item.data(Qt.ItemDataRole.UserRole)
                self.mouseLeftEmoji.emit(emoji, item)
            self.__last_index = None

        # Se o mouse entrou num novo item
        if index.isValid() and index != self.__last_index:
            self.__last_index = index
            item = self.__get_item_from_index(index)
            if item:
                emoji = item.data(Qt.ItemDataRole.UserRole)
                self.mouseEnteredEmoji.emit(emoji, item)

    def leaveEvent(self, e: QEvent):
        """Garante que o sinal de saída seja emitido ao sair do widget."""
        if self.__last_index:
            item = self.__get_item_from_index(self.__last_index)
            if item:
                emoji = item.data(Qt.ItemDataRole.UserRole)
                self.mouseLeftEmoji.emit(emoji, item)
            self.__last_index = None
        super().leaveEvent(e)

    def mouseReleaseEvent(self, e: QMouseEvent):
        """Gerencia o clique."""
        super().mouseReleaseEvent(e)
        if e.button() == Qt.MouseButton.LeftButton:
            index = self.indexAt(e.pos())
            if index.isValid():
                item = self.__get_item_from_index(index)
                emoji = item.data(Qt.ItemDataRole.UserRole)
                self.emojiClicked.emit(emoji, item)

    def contextMenuEvent(self, e):
        """Gerencia menu de contexto."""
        index = self.indexAt(e.pos())
        if index.isValid():
            item = self.__get_item_from_index(index)
            emoji = item.data(Qt.ItemDataRole.UserRole)
            self.contextMenu.emit(emoji, item, self.mapToGlobal(e.pos()))

    # --- Métodos Privados Auxiliares ---

    def __get_item_from_index(self, index):
        # Se estiver usando proxy, precisa mapear
        if isinstance(index.model(), QAbstractProxyModel):
            index = self.__proxy.mapToSource(index)
        return self.__model.itemFromIndex(index)

    @staticmethod
    def _create_emoji_item(emoji: Emoji) -> QStandardItem:
        item = QStandardItem()
        item.setData(emoji, Qt.ItemDataRole.UserRole)
        item.setEditable(False)
        return item

    def __treat_limit(self):
        if self.__limit_treatment == self.LimitTreatment.RemoveFirstOne:
            self.__model.removeRow(0)
        elif self.__limit_treatment == self.LimitTreatment.RemoveLastOne:
            self.__model.removeRow(self.__model.rowCount() - 1)

    # --- API Pública (camelCase) ---
    def addEmoji(self, emoji: Emoji, update_geometry: bool = True):
        """Adiciona um item ao modelo."""
        if self.__model.rowCount() + 1 > self.__limit:
            self.__treat_limit()

        if self.__model.rowCount() < self.__limit:
            self.__model.appendRow(self._create_emoji_item(emoji))
            # Chama ajuste de altura após adicionar (pode ser otimizado para chamar só uma vez no final)
            if update_geometry:
                self.updateGeometry()

    def emojiItem(self, emoji: Emoji) -> typing.Optional[QStandardItem]:
        start_index = self.__model.index(0, 0)
        matches = self.__model.match(start_index, Qt.ItemDataRole.UserRole, emoji, 1, Qt.MatchFlag.MatchExactly)
        if matches:
            return matches[0]
        return None

    def removeEmoji(self, emoji: Emoji, update_geometry: bool = True):
        """Remove um emoji específico."""
        # A lógica de busca depende de como o dado está guardado.
        # Exemplo simples iterando (lento para muitos itens, ideal seria um dict de mapeamento)
        match = self.emojiItem(emoji)
        if match:
            self.__model.removeRow(match.row())
            if update_geometry:
                self.updateGeometry()

    def allFiltered(self) -> bool:
        """Retorna True se todos os itens estiverem filtrados (escondidos pelo Proxy)."""
        return self.__proxy.rowCount() == 0

    def filterContent(self, text: str):
        """Aplica filtro."""
        self.__proxy.setFilterFixedString(text)
        self.updateGeometry() # Reajusta altura baseado no que sobrou

    def setLimit(self, limit: int):
        self.__limit = limit

    def limit(self):
        return self.__limit

    def setLimitTreatment(self, limit_treatment: typing.Optional[LimitTreatment]):
        self.__limit_treatment = limit_treatment

    def limitTreatment(self) -> LimitTreatment:
        return self.__limit_treatment