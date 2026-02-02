import typing
from functools import partial

from PySide6.QtCore import QSize, QModelIndex, Signal, QPoint, Qt, QTimer, Slot, QPersistentModelIndex
from PySide6.QtGui import QFont, QIcon, QFontMetrics, QPixmap
from PySide6.QtWidgets import (QLineEdit, QHBoxLayout, QLabel, QVBoxLayout,
                               QWidget, QButtonGroup, QMenu, QToolButton, QApplication)

from qextrawidgets.delegates.grouped_icon_delegate import QGroupedIconDelegate
from qextrawidgets.emoji_utils import EmojiImageProvider
from qextrawidgets.items.emoji_category_item import QEmojiCategoryItem
from qextrawidgets.models.emoji_picker_model import EmojiCategory, QEmojiPickerModel
from qextrawidgets.proxys.emoji_picker_proxy import QEmojiPickerProxyModel
from qextrawidgets.utils import char_to_pixmap
from qextrawidgets.views.grouped_icon_view import QGroupedIconView
from qextrawidgets.widgets.accordion.accordion_item import QAccordionItem
from qextrawidgets.items.emoji_item import QEmojiDataRole, QEmojiItem, EmojiSkinTone
from qextrawidgets.widgets.icon_combo_box import QIconComboBox
from qextrawidgets.widgets.search_line_edit import QSearchLineEdit


class QEmojiPicker(QWidget):
    """A comprehensive emoji picker widget.

    Features categories, search, skin tone selection, and recent/favorite emojis.

    Signals:
        picked (str): Emitted when an emoji is selected.
    """

    picked = Signal(str)

    def __init__(
            self,
            model: typing.Optional[QEmojiPickerModel] = None,
            emoji_pixmap_getter: typing.Union[str, QFont, typing.Callable[[str], QPixmap]] = partial(EmojiImageProvider.getPixmap, margin=0, size=128),
            emoji_label_size: QSize = QSize(32, 32)) -> None:
        """Initializes the emoji picker.

        Args:
            model (QEmojiModel, optional): Custom emoji model. Defaults to None.
        """
        super().__init__()

        self._skin_tone_selector_emojis = {
            EmojiSkinTone.Default: "👏",
            EmojiSkinTone.Light: "👏🏻",
            EmojiSkinTone.MediumLight: "👏🏼",
            EmojiSkinTone.Medium: "👏🏽",
            EmojiSkinTone.MediumDark: "👏🏾",
            EmojiSkinTone.Dark: "👏🏿"
        }

        if model:
            self._model = model
        else:
            self._model = QEmojiPickerModel()

        self._proxy = QEmojiPickerProxyModel()
        self._proxy.setSourceModel(self._model)

        self._search_line_edit = self._create_search_line_edit()

        self._grouped_icon_view = QGroupedIconView(self, QSize(40, 40), 5)
        self._grouped_icon_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._grouped_icon_view.setModel(self._proxy)

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(200)

        self._skin_tone_selector = QIconComboBox()

        for skin_tone, emoji in self._skin_tone_selector_emojis.items():
            self._skin_tone_selector.addItem(text=emoji, data=skin_tone)

        self._shortcuts_container = QWidget()
        self._shortcuts_container.setFixedHeight(40)  # Fixed height for the bar

        self._shortcuts_group = QButtonGroup(self)
        self._shortcuts_group.setExclusive(True)

        self._emoji_on_label = None

        self._emoji_label = QLabel()
        self._emoji_label.setFixedSize(emoji_label_size)
        self._emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._emoji_label.setScaledContents(True)

        self._aliases_emoji_label = self._create_emoji_label()

        self._setup_layout()
        self._setup_connections()

        if model is None:
            self._model.populate()

        self._emoji_pixmap_getter = None
        self.setEmojiPixmapGetter(emoji_pixmap_getter)

        self.translateUI()

    def _setup_layout(self) -> None:
        """Sets up the initial layout of the widget."""
        self._shortcuts_layout = QHBoxLayout(self._shortcuts_container)
        self._shortcuts_layout.setContentsMargins(5, 0, 5, 0)
        self._shortcuts_layout.setSpacing(2)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self._search_line_edit, True)
        header_layout.addWidget(self._skin_tone_selector)

        content_layout = QHBoxLayout()
        content_layout.addWidget(self._emoji_label)
        content_layout.addWidget(self._aliases_emoji_label, True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self._shortcuts_container)
        main_layout.addWidget(self._grouped_icon_view)
        main_layout.addLayout(content_layout)

    def _setup_connections(self) -> None:
        """Sets up signals and slots connections."""
        self._search_timer.timeout.connect(self._on_filter_emojis)
        self._search_line_edit.textChanged.connect(lambda: self._search_timer.start())

        self._model.categoryInserted.connect(self._on_categories_inserted)
        self._grouped_icon_view.itemEntered.connect(self._on_mouse_entered_emoji)
        self._grouped_icon_view.itemExited.connect(self._on_mouse_exited_emoji)
        self._grouped_icon_view.itemClicked.connect(self._on_item_clicked)
        self._grouped_icon_view.customContextMenuRequested.connect(self._on_context_menu)

        self._skin_tone_selector.currentDataChanged.connect(self._on_set_skin_tone)

        delegate: QGroupedIconDelegate = self._grouped_icon_view.itemDelegate()
        delegate.requestImage.connect(self._on_request_image)

        self._model.skinToneChanged.connect(delegate.forceReload)

    @Slot(str)
    def _on_set_skin_tone(self, skin_tone: str) -> None:
        """Updates the skin tone of the emojis.

        Args:
            skin_tone (str): Skin tone modifier.
        """
        print(skin_tone)
        self._model.setSkinTone(skin_tone)

    @Slot(QModelIndex)
    def _on_item_clicked(self, proxy_index: QModelIndex):
        source_index = self._proxy.mapToSource(proxy_index)
        item: QEmojiItem = self._model.itemFromIndex(source_index)
        self.picked.emit(item.emoji())

        recent_category_index = self._model.findCategory(EmojiCategory.Recents)
        if recent_category_index:
            recent_item_index = self._model.findEmojiInCategory(recent_category_index, item.emoji())
            if not recent_item_index:
                clone_item = item.clone()
                clone_item.setData(EmojiCategory.Recents, role=QEmojiDataRole.CategoryRole)
                self._model.itemFromIndex(recent_category_index).appendRow(clone_item)

    @Slot(QPoint)
    def _on_context_menu(self, position: QPoint) -> None:
        """Handles the context menu for an emoji.

        Args:
            grid (QEmojiGrid): The grid where the event occurred.
            position (QPoint): Pixel position.
        """
        proxy_index = self._grouped_icon_view.indexAt(position)
        source_index = self._proxy.mapToSource(proxy_index)
        item = self._model.itemFromIndex(source_index)

        menu = QMenu(self._grouped_icon_view)

        if isinstance(item, QEmojiCategoryItem):
            collapse_all_action = menu.addAction(self.tr("Collapse all"))
            collapse_all_action.triggered.connect(lambda: self._model.setExpanded(False))
            expand_all_action = menu.addAction(self.tr("Expand all"))
            expand_all_action.triggered.connect(lambda: self._model.setExpanded(True))
        elif isinstance(item, QEmojiItem):
            favorite_category_index: QModelIndex = self._model.findCategory(EmojiCategory.Favorites)
            if favorite_category_index:
                favorite_item_index: QModelIndex = self._model.findEmojiInCategory(favorite_category_index, item.emoji())
                favorite_category_item: QEmojiCategoryItem = self._model.itemFromIndex(favorite_category_index)
                if favorite_item_index:
                    action = menu.addAction(self.tr("Unfavorite"))
                    row = favorite_item_index.row()
                    action.triggered.connect(lambda: favorite_category_item.removeRow(row))
                else:
                    action = menu.addAction(self.tr("Favorite"))
                    clone_item = item.clone()
                    clone_item.setData(EmojiCategory.Favorites, role=QEmojiDataRole.CategoryRole)
                    action.triggered.connect(lambda: favorite_category_item.appendRow(clone_item))

            copy_alias_action = menu.addAction(self.tr("Copy alias"))
            clipboard = QApplication.clipboard()
            copy_alias_action.triggered.connect(lambda: clipboard.setText(item.firstAlias()))
        else:
            return

        menu.exec(self._grouped_icon_view.mapToGlobal(position))

    @Slot(QPersistentModelIndex)
    def _on_request_image(self, persistent_index: QPersistentModelIndex):
        # 1. Converta explicitamente para QModelIndex (Segurança de Tipo)
        proxy_index = QModelIndex(persistent_index)

        if not proxy_index.isValid():
            return

        # 2. Mapeia do Proxy para o Modelo Original
        source_index = self._proxy.mapToSource(proxy_index)

        if not source_index.isValid():
            return

        # 3. Busca o item e define a imagem
        item: QEmojiItem = self._model.itemFromIndex(source_index)
        if item:
            # Gera o pixmap
            pixmap = self.emojiPixmapGetter()(item.emoji())

            # Debug: Garante que o pixmap foi gerado
            if pixmap.isNull():
                print(f"ALERTA: Pixmap nulo gerado para {item.emoji()}")

            # Seta o ícone (Isso dispara o dataChanged no model -> proxy -> view)
            item.setIcon(pixmap)

    @Slot(QEmojiCategoryItem)
    def _on_categories_inserted(self, category_item: QEmojiCategoryItem) -> None:
        """Handles the insertion of categories into the model."""
        category = category_item.text()
        icon = category_item.icon()

        shortcut = self._create_shortcut_button(category, icon)
        shortcut.setObjectName(category)
        shortcut.clicked.connect(lambda: self._on_shortcut_clicked(category_item.index()))

        self._shortcuts_layout.addWidget(shortcut)
        self._shortcuts_group.addButton(shortcut)

    # @Slot(QModelIndex, int, int)
    # def _on_categories_removed(self, _: QModelIndex, first: int, last: int) -> None:
    #     """Handles the removal of categories from the model."""
    #     for row in range(first, last + 1):
    #         item = self._category_model.item(row)
    #         if not item:
    #             continue
    #
    #         category = item.data(QEmojiDataRole.CategoryRole)
    #
    #         section = self.accordion().item(category)
    #         grid: QEmojiGridView = section.content()
    #         shortcut = self._shortcuts_container.findChild(QToolButton, category)
    #         proxy = grid.model()
    #
    #         self._accordion.removeAccordionItem(section)
    #         self._shortcuts_layout.removeWidget(shortcut)
    #         self._shortcuts_group.removeButton(shortcut)
    #
    #         section.deleteLater()
    #         grid.deleteLater()
    #         shortcut.deleteLater()
    #         proxy.deleteLater()

    @Slot(QModelIndex)
    def _on_mouse_entered_emoji(self, index: QModelIndex) -> None:
        source_index = self._proxy.mapToSource(index)
        item: QEmojiItem = self._model.itemFromIndex(source_index)
        if isinstance(item, QEmojiItem):
            self._emoji_on_label = item.emoji()
            self._paint_emoji_on_label()
            metrics = QFontMetrics(self._aliases_emoji_label.font())
            aliases_text = item.aliasesText()
            elided_alias = metrics.elidedText(aliases_text, Qt.TextElideMode.ElideRight, self._aliases_emoji_label.width())
            self._aliases_emoji_label.setText(elided_alias)

    @Slot(QModelIndex)
    def _on_shortcut_clicked(self, source_index: QModelIndex) -> None:
        """Scrolls the accordion to the selected category section.

        Args:
            section (QAccordionItem): The section to scroll to.
        """
        proxy_index = self._proxy.mapFromSource(source_index)
        self._grouped_icon_view.scrollTo(proxy_index)

    @Slot()
    def _on_filter_emojis(self) -> None:
        """Filters the emojis across all categories based on the search text."""
        text = self._search_line_edit.text()
        self._proxy.setFilterFixedString(text)

    @Slot()
    def _on_mouse_exited_emoji(self) -> None:
        """Clears the emoji preview area."""
        self._emoji_label.clear()
        self._aliases_emoji_label.clear()
        self._emoji_on_label = None

    @staticmethod
    def _create_search_line_edit() -> QLineEdit:
        """Creates and configures a search line edit.

        Returns:
            QLineEdit: The configured search line edit.
        """
        font = QFont()
        font.setPointSize(12)
        line_edit = QSearchLineEdit()
        line_edit.setFont(font)
        return line_edit

    @staticmethod
    def _create_emoji_label() -> QLabel:
        """Creates and configures the emoji alias label.

        Returns:
            QLabel: The configured alias label.
        """
        font = QFont()
        font.setBold(True)
        font.setPointSize(13)
        label = QLabel()
        label.setFont(font)
        return label

    @staticmethod
    def _create_shortcut_button(text: str, icon: QIcon) -> QToolButton:
        """Creates a shortcut button for the category bar.

        Args:
            text (str): Tooltip text.
            icon (QIcon): Button icon.

        Returns:
            QToolButton: The configured shortcut button.
        """
        btn = QToolButton()
        btn.setCheckable(True)
        btn.setAutoRaise(True)
        btn.setFixedSize(32, 32)
        btn.setIconSize(QSize(22, 22))
        btn.setToolTip(text)
        btn.setText(text)
        btn.setIcon(icon)
        return btn

    def _paint_emoji_on_label(self):
        if self._emoji_on_label:
            pixmap = self.emojiPixmapGetter()(self._emoji_on_label)
            self._emoji_label.setPixmap(pixmap)

    def _paint_skintones(self):
        emoji_pixmap_getter = self.emojiPixmapGetter()
        for index, emoji in enumerate(self._skin_tone_selector_emojis.values()):
            self._skin_tone_selector.setItemIcon(index, emoji_pixmap_getter(emoji))

    # --- Public API (camelCase) ---

    def translateUI(self) -> None:
        """Translates the UI components."""
        self._search_line_edit.setPlaceholderText(self.tr("Search emoji..."))

    def resetPicker(self) -> None:
        """Resets the picker state."""
        self._search_line_edit.clear()

    def setEmojiPixmapGetter(self, emoji_pixmap_getter: typing.Union[str, QFont, typing.Callable[[str], QPixmap]]):
        if isinstance(emoji_pixmap_getter, str):
            font_family = emoji_pixmap_getter
        elif isinstance(emoji_pixmap_getter, QFont):
            font_family = emoji_pixmap_getter.family()
        else:
            font_family = None

        if font_family:
            emoji_font = QFont()
            emoji_font.setFamily(font_family)
            emoji_font.setPixelSize(48)
            self._emoji_pixmap_getter = partial(char_to_pixmap, font=emoji_font)
        else:
            self._emoji_pixmap_getter = emoji_pixmap_getter

        self._paint_emoji_on_label()
        self._paint_skintones()

    def emojiPixmapGetter(self):
        return self._emoji_pixmap_getter