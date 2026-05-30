"""
demo_emoji_view.py
==================
Demo interativo para QEmojiView.

Funcionalidades demonstradas:
- Exibição de emojis em grade via QEmojiView
- Filtragem em tempo real por texto (busca no EditRole)
- Filtro por categoria (via QSortFilterProxyModel customizado)
- Alternância entre fontes de renderização (PNG / SVG / Fonte do sistema)
- Ajuste dinâmico do tamanho dos ícones
- Seleção de emoji com exibição do caractere e codepoint

Arquitetura dos modelos:
    QStandardItemModel          <- dados brutos (emoji + categoria)
        |
    EmojiFilterProxyModel       <- filtra por texto e/ou categoria
        |
    QDecorationRoleProxyModel   <- armazena pixmaps sem tocar no modelo fonte
        |
    QEmojiView                  <- renderiza a grade

Execução:
    python demo_emoji_view.py
"""

import sys
import unicodedata

from PySide6.QtCore import Qt, QSortFilterProxyModel, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QSlider,
    QGroupBox,
    QStatusBar,
    QSizePolicy,
    QFrame,
    QToolButton,
)

from qextrawidgets.gui.proxys import QDecorationRoleProxyModel
from qextrawidgets.widgets.views import QEmojiView


# ---------------------------------------------------------------------------
# Role customizada para categoria
# ---------------------------------------------------------------------------

CATEGORY_ROLE = Qt.ItemDataRole.UserRole + 1


# ---------------------------------------------------------------------------
# Proxy de filtro customizado — filtra por texto (EditRole) e categoria
# ---------------------------------------------------------------------------

class EmojiFilterProxyModel(QSortFilterProxyModel):
    """Filtra emojis por texto de busca e/ou categoria.

    O filtro de texto compara contra o EditRole (caractere emoji).
    O filtro de categoria compara contra o CATEGORY_ROLE.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._category_filter: str = ""  # "" = todas

    def setCategory(self, category: str) -> None:
        self._category_filter = category if category != "Todas" else ""
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        index = self.sourceModel().index(source_row, 0, source_parent)

        # Filtro de categoria
        if self._category_filter:
            if index.data(CATEGORY_ROLE) != self._category_filter:
                return False

        # Filtro de texto (busca no caractere emoji via EditRole)
        pattern = self.filterRegularExpression().pattern()
        if pattern:
            emoji = index.data(Qt.ItemDataRole.EditRole) or ""
            if pattern.lower() not in emoji.lower():
                return False

        return True


# ---------------------------------------------------------------------------
# Dados de exemplo — subconjunto de emojis agrupados por categoria
# ---------------------------------------------------------------------------

EMOJI_CATEGORIES: dict[str, list[str]] = {
    "Rostos": [
        "😀", "😁", "😂", "🤣", "😃", "😄", "😅", "😆", "😇", "😈",
        "😉", "😊", "😋", "😌", "😍", "🥰", "😎", "🤓", "🧐", "😏",
        "😒", "😞", "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫",
        "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬", "🤯", "😳",
        "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗", "🤔", "🤭",
        "🤫", "🤥", "😶", "😐", "😑", "😬", "🙄", "😯", "😦", "😧",
        "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐", "🥴", "🤢",
        "🤮", "🤧", "😷", "🤒", "🤕",
    ],
    "Gestos": [
        "👋", "🤚", "🖐️", "✋", "🖖", "👌", "🤌", "🤏", "✌️", "🤞",
        "🤟", "🤘", "🤙", "👈", "👉", "👆", "🖕", "👇", "☝️", "👍",
        "👎", "✊", "👊", "🤛", "🤜", "👏", "🙌", "👐", "🤲", "🤝",
        "🙏", "✍️", "💅", "🤳", "💪", "🦾", "🦿", "🦵", "🦶",
    ],
    "Animais": [
        "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐻‍❄️", "🐨",
        "🐯", "🦁", "🐮", "🐷", "🐸", "🐵", "🙈", "🙉", "🙊", "🐔",
        "🐧", "🐦", "🐤", "🦆", "🦅", "🦉", "🦇", "🐺", "🐗", "🐴",
        "🦄", "🐝", "🪱", "🐛", "🦋", "🐌", "🐞", "🐜", "🪲", "🦟",
        "🦗", "🪰", "🦂", "🐢", "🐍", "🦎", "🦖", "🦕", "🐊", "🐸",
        "🦓", "🦍", "🦧", "🦣", "🐘", "🦛", "🦏", "🐪", "🐫", "🦒",
        "🦘", "🦬", "🐃", "🐂", "🐄", "🐎", "🐖", "🐏", "🐑", "🦙",
        "🐐", "🦌", "🐕", "🐩", "🦮", "🐕‍🦺", "🐈", "🐈‍⬛", "🐓", "🦃",
    ],
    "Comidas": [
        "🍎", "🍊", "🍋", "🍇", "🍓", "🫐", "🍈", "🍒", "🍑", "🥭",
        "🍍", "🥥", "🥝", "🍅", "🍆", "🥑", "🫑", "🥦", "🥬", "🥒",
        "🌽", "🥕", "🧄", "🧅", "🥔", "🍠", "🧇", "🥞", "🧈", "🍳",
        "🥚", "🧀", "🥗", "🥙", "🌮", "🌯", "🥪", "🍕", "🍔", "🍟",
        "🌭", "🍿", "🍦", "🍧", "🍨", "🍩", "🍪", "🎂", "🍰", "🧁",
        "🍫", "🍬", "🍭", "☕", "🍵", "🧃", "🥤", "🧋", "🍺", "🍻",
    ],
    "Objetos": [
        "⌚", "📱", "💻", "⌨️", "🖥️", "🖨️", "🖱️", "📷", "📸", "📹",
        "🎥", "📞", "☎️", "📟", "📠", "📺", "📻", "🧭", "⏱️", "⏰",
        "📡", "🔋", "🔌", "💡", "🔦", "🕯️", "🪔", "🧯", "🛢️", "💰",
        "💳", "🪙", "💎", "⚖️", "🔧", "🔨", "⚒️", "🛠️", "🔩", "⚙️",
        "🔗", "⛓️", "🧲", "🔫", "💣", "🪓", "🔪", "🗡️", "⚔️", "🛡️",
        "🚪", "🪞", "🪟", "🛋️", "🪑", "🚽", "🧻", "🚿", "🛁",
    ],
    "Símbolos": [
        "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔",
        "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "✨", "⭐",
        "🌟", "💫", "⚡", "🌈", "🔥", "💧", "❄️", "🌊", "💥", "🎉",
        "🎊", "🎈", "🎁", "🏆", "🥇", "🥈", "🥉", "🎯", "🎮", "🎲",
        "♠️", "♥️", "♦️", "♣️", "🃏", "🀄", "♟️", "✅", "❌", "⭕",
        "🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "⚫", "⚪", "🟤",
    ],
}

ALL_CATEGORIES = ["Todas"] + list(EMOJI_CATEGORIES.keys())


# ---------------------------------------------------------------------------
# Janela principal
# ---------------------------------------------------------------------------

class EmojiDemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QEmojiView — Demo")
        self.resize(800, 620)

        # ------------------------------------------------------------------
        # Cadeia de modelos:
        #   QStandardItemModel
        #       -> EmojiFilterProxyModel
        #           -> QDecorationRoleProxyModel  <- passado ao QEmojiView
        #
        # O QDecorationRoleProxyModel NÃO é criado internamente pelo
        # QEmojiView neste fluxo — ele é construído aqui para que possamos
        # encadear o proxy de filtro antes dele, sem perder a separação de
        # responsabilidades (o decoration proxy nunca toca no modelo fonte).
        # ------------------------------------------------------------------
        self._source_model = QStandardItemModel()
        self._build_model()

        self._filter_proxy = EmojiFilterProxyModel()
        self._filter_proxy.setSourceModel(self._source_model)

        self._decoration_proxy = QDecorationRoleProxyModel()
        self._decoration_proxy.setSourceModel(self._filter_proxy)

        # ------------------------------------------------------------------
        # Layout
        # ------------------------------------------------------------------
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 8)
        root_layout.setSpacing(8)

        root_layout.addWidget(self._build_controls())

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        root_layout.addWidget(sep)

        # QEmojiView recebe o QDecorationRoleProxyModel já configurado.
        # Internamente o view não cria um segundo decoration proxy — ele usa
        # o que for passado via setModel().
        self._emoji_view = QEmojiView()
        self._emoji_view.setModel(self._decoration_proxy)
        self._emoji_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root_layout.addWidget(self._emoji_view)

        root_layout.addWidget(self._build_detail_panel())

        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._update_status()

        # ------------------------------------------------------------------
        # Conexões
        # ------------------------------------------------------------------
        self._emoji_view.itemClicked.connect(self._on_item_clicked)
        self._filter_proxy.rowsInserted.connect(self._update_status)
        self._filter_proxy.rowsRemoved.connect(self._update_status)
        self._filter_proxy.modelReset.connect(self._update_status)

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_controls(self) -> QWidget:
        """Constrói a barra de controles: busca, categoria, renderização, tamanho."""
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("🔍  Buscar emoji…")
        self._search_edit.setClearButtonEnabled(True)
        self._search_edit.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search_edit, stretch=3)

        layout.addWidget(QLabel("Categoria:"))
        self._category_combo = QComboBox()
        self._category_combo.addItems(ALL_CATEGORIES)
        self._category_combo.currentTextChanged.connect(self._on_category_changed)
        layout.addWidget(self._category_combo, stretch=1)

        layout.addWidget(QLabel("Renderização:"))
        self._source_combo = QComboBox()
        self._source_combo.addItems(["PNG (Twemoji)", "SVG (Twemoji)", "Fonte do sistema"])
        self._source_combo.currentIndexChanged.connect(self._on_source_changed)
        layout.addWidget(self._source_combo, stretch=1)

        layout.addWidget(QLabel("Tamanho:"))
        self._size_slider = QSlider(Qt.Orientation.Horizontal)
        self._size_slider.setRange(24, 96)
        self._size_slider.setValue(48)
        self._size_slider.setTickInterval(8)
        self._size_slider.setFixedWidth(120)
        self._size_label = QLabel("48 px")
        self._size_label.setFixedWidth(42)
        self._size_slider.valueChanged.connect(self._on_size_changed)
        layout.addWidget(self._size_slider)
        layout.addWidget(self._size_label)

        return bar

    def _build_detail_panel(self) -> QGroupBox:
        """Constrói o painel inferior com detalhes do emoji selecionado."""
        group = QGroupBox("Emoji selecionado")
        layout = QHBoxLayout(group)
        layout.setSpacing(16)

        self._preview_label = QLabel("—")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setStyleSheet("font-size: 48px;")
        self._preview_label.setFixedSize(72, 72)
        layout.addWidget(self._preview_label)

        details_layout = QVBoxLayout()
        self._char_label = QLabel("Nenhum emoji selecionado")
        self._char_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self._codepoint_label = QLabel("")
        self._name_label = QLabel("")
        details_layout.addWidget(self._char_label)
        details_layout.addWidget(self._codepoint_label)
        details_layout.addWidget(self._name_label)
        details_layout.addStretch()
        layout.addLayout(details_layout, stretch=1)

        self._copy_btn = QToolButton()
        self._copy_btn.setText("📋 Copiar")
        self._copy_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._copy_btn.setEnabled(False)
        self._copy_btn.clicked.connect(self._on_copy_emoji)
        layout.addWidget(self._copy_btn)

        self._selected_emoji: str = ""
        return group

    # ------------------------------------------------------------------
    # Modelo
    # ------------------------------------------------------------------

    def _build_model(self) -> None:
        """Popula o QStandardItemModel com todos os emojis e suas categorias."""
        self._source_model.clear()
        for category, emojis in EMOJI_CATEGORIES.items():
            for emoji in emojis:
                item = QStandardItem()
                item.setEditable(False)
                item.setData(emoji, Qt.ItemDataRole.EditRole)
                item.setData(category, CATEGORY_ROLE)
                try:
                    name = unicodedata.name(emoji[0], emoji)
                except (ValueError, TypeError):
                    name = emoji
                item.setToolTip(f"{emoji}  {name}")
                self._source_model.appendRow(item)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_search_changed(self, text: str) -> None:
        self._filter_proxy.setFilterFixedString(text)
        self._update_status()

    def _on_category_changed(self, category: str) -> None:
        self._filter_proxy.setCategory(category)
        self._update_status()

    def _on_source_changed(self, index: int) -> None:
        provider = getattr(self._emoji_view, "_emoji_image_provider", None)
        if provider is None:
            return
        sources = ["png", "svg", "Segoe UI Emoji"]
        provider.setSource(sources[index])

    def _on_size_changed(self, value: int) -> None:
        from PySide6.QtCore import QSize
        self._size_label.setText(f"{value} px")
        self._emoji_view.setIconSize(QSize(value, value))

    def _on_item_clicked(self, index: QModelIndex) -> None:
        """Exibe detalhes do emoji clicado.

        O index recebido aponta para o QDecorationRoleProxyModel.
        É necessário mapear dois níveis até o QStandardItemModel para
        ler os dados sem intermediários.
        """
        # decoration proxy -> filter proxy -> source model
        filter_index = self._decoration_proxy.mapToSource(index)
        source_index = self._filter_proxy.mapToSource(filter_index)

        emoji = source_index.data(Qt.ItemDataRole.EditRole)
        if not emoji:
            return

        self._selected_emoji = emoji
        self._preview_label.setText(emoji)

        codepoints = " ".join(f"U+{ord(c):04X}" for c in emoji if c != "\uFE0F")
        self._codepoint_label.setText(f"Codepoint: {codepoints}")

        try:
            name = unicodedata.name(emoji[0])
        except (ValueError, TypeError):
            name = "—"
        self._name_label.setText(f"Nome: {name}")
        self._char_label.setText(emoji)
        self._copy_btn.setEnabled(True)

    def _on_copy_emoji(self) -> None:
        if self._selected_emoji:
            QApplication.clipboard().setText(self._selected_emoji)
            self._status.showMessage(
                f"'{self._selected_emoji}' copiado para a área de transferência!", 2500
            )

    def _update_status(self) -> None:
        total = self._filter_proxy.rowCount()
        self._status.showMessage(f"{total} emoji(s) exibido(s)")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("QEmojiView Demo")
    app.setStyle("Fusion")

    window = EmojiDemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()