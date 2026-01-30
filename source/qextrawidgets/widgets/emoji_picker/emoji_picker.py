import typing

from PySide6.QtCore import QSize, QModelIndex, Signal, QPoint, Qt, QTimer, Slot
from PySide6.QtGui import QFont, QIcon, QFontMetrics, QPixmap
from PySide6.QtWidgets import (QLineEdit, QHBoxLayout, QLabel, QVBoxLayout,
                               QWidget, QButtonGroup, QMenu, QToolButton, QApplication)

from qextrawidgets.utils import get_max_pixel_size
from qextrawidgets.widgets.accordion import QAccordion
from qextrawidgets.widgets.accordion.accordion_item import QAccordionItem
from qextrawidgets.widgets.emoji_picker.category_model import QEmojiCategoryModel
from qextrawidgets.widgets.emoji_picker.emoji_delegate import QEmojiDelegate
from qextrawidgets.widgets.emoji_picker.emoji_grid import QEmojiGrid
from qextrawidgets.widgets.emoji_picker.emoji_model import QEmojiModel
from qextrawidgets.widgets.emoji_picker.emoji_sort_filter import QEmojiSortFilterProxyModel
from qextrawidgets.widgets.emoji_picker.enums import QEmojiDataRole, EmojiSkinTone, EmojiCategory
from qextrawidgets.widgets.icon_combo_box import QIconComboBox
from qextrawidgets.widgets.search_line_edit import QSearchLineEdit


class QEmojiPicker(QWidget):
    """A comprehensive emoji picker widget.

    Features categories, search, skin tone selection, and recent/favorite emojis.

    Signals:
        picked (str): Emitted when an emoji is selected.
    """

    picked = Signal(str)

    def __init__(self,
                 model: typing.Optional[QEmojiModel] = None,
                 category_model: typing.Optional[QEmojiCategoryModel] = None,
                 delegate: typing.Optional[QEmojiDelegate] = None,
                 emoji_label_size: QSize = QSize(32, 32)) -> None:
        """Initializes the emoji picker.

        Args:
            model (QEmojiModel, optional): Custom emoji model. Defaults to None.
            category_model (QEmojiCategoryModel, optional): Custom category model. Defaults to None.
            delegate (QEmojiDelegate, optional): Custom emoji delegate. Defaults to None.
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
            self._model = QEmojiModel()
            self._model.populate()

        if category_model:
            self._category_model = category_model
        else:
            self._category_model = QEmojiCategoryModel(self)

        self._accordion = QAccordion()

        # 1. Search Bar
        self._search_line_edit = self._create_search_line_edit()

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

        self._emoji_label = QLabel()
        self._emoji_label.setFixedSize(emoji_label_size)
        self._emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._emoji_label.setScaledContents(True)

        self._aliases_emoji_label = self._create_emoji_label()
        self._emoji_on_label = None

        if delegate:
            self._delegate = delegate
        else:
            self._delegate = QEmojiDelegate(self)

        self._setup_layout()
        self._setup_connections()

        if not category_model:
            self._category_model.populate()

        self._on_emoji_font_changed(self._delegate.emojiFont())

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
        main_layout.addWidget(self._accordion)
        main_layout.addLayout(content_layout)

    def _setup_connections(self) -> None:
        """Sets up signals and slots connections."""
        self._search_timer.timeout.connect(self._on_filter_emojis)
        self._search_line_edit.textChanged.connect(lambda: self._search_timer.start())
        self._accordion.enteredSection.connect(self._on_entered_section)
        self._skin_tone_selector.currentDataChanged.connect(self._on_set_skin_tone)

        self._category_model.rowsInserted.connect(self._on_categories_inserted)
        self._category_model.rowsAboutToBeRemoved.connect(self._on_categories_removed)
        
        self._delegate.emojiSizeChanged.connect(self._on_emoji_size_changed)
        self._delegate.emojiPixmapGetterChanged.connect(self._on_emoji_pixmap_getter_changed)
        self._delegate.emojiFontChanged.connect(self._on_emoji_font_changed)

    @Slot(str)
    def _on_emoji_font_changed(self, font_family: str) -> None:
        font = QFont(font_family)
        font.setPixelSize(get_max_pixel_size("👏", font_family, self._emoji_label.size()))
        self._emoji_label.setFont(font)
        for index in range(len(self._skin_tone_selector_emojis)):
            self._skin_tone_selector.setItemFont(index, font_family)

    @Slot()
    def _on_emoji_pixmap_getter_changed(self):
        self._redraw_skintones()
        self._redraw_alias_emoji()

    @Slot(str)
    def _on_set_skin_tone(self, skin_tone: str) -> None:
        """Updates the skin tone of the emojis.

        Args:
            skin_tone (str): Skin tone modifier.
        """
        self._model.setSkinTone(skin_tone)

    @Slot(QModelIndex, int, int)
    def _on_categories_inserted(self, _: QModelIndex, first: int, last: int) -> None:
        """Handles the insertion of categories into the model."""
        for row in range(first, last + 1):
            item = self._category_model.item(row)
            if not item:
                continue

            category = item.data(QEmojiDataRole.CategoryRole)
            text = item.text()
            icon = item.icon()

            # Grid
            grid = self._create_grid()

            # Proxy
            proxy = grid.model()
            proxy.setCategoryFilter(text)
            proxy.setSourceModel(self.model())

            if category == EmojiCategory.Favorites:
                proxy.setFavoriteFilter(True)
                proxy.setCategoryFilter(None)

            if category == EmojiCategory.Recents:
                proxy.setRecentFilter(True)
                proxy.setCategoryFilter(None)

            # Category Section
            section = self._accordion.insertSection(text, grid, row, True, category)

            shortcut = self._create_shortcut_button(text, icon)
            shortcut.setObjectName(category)
            self._shortcuts_layout.insertWidget(row, shortcut)
            self._shortcuts_group.addButton(shortcut)

            # Connections
            shortcut.clicked.connect(lambda checked=False, s=section: self._on_shortcut_clicked(s))
            grid.entered.connect(self._on_hover_emoji)
            grid.left.connect(self._on_clear_emoji_preview)
            grid.clicked.connect(self._on_emoji_clicked)
            grid.customContextMenuRequested.connect(lambda pos, g=grid: self._on_context_menu(g, pos))

    @Slot(QModelIndex, int, int)
    def _on_categories_removed(self, _: QModelIndex, first: int, last: int) -> None:
        """Handles the removal of categories from the model."""
        for row in range(first, last + 1):
            item = self._category_model.item(row)
            if not item:
                continue

            category = item.data(QEmojiDataRole.CategoryRole)

            section = self.accordion().item(category)
            grid: QEmojiGrid = section.content()
            shortcut = self._shortcuts_container.findChild(QToolButton, category)
            proxy = grid.model()

            self._accordion.removeAccordionItem(section)
            self._shortcuts_layout.removeWidget(shortcut)
            self._shortcuts_group.removeButton(shortcut)

            section.deleteLater()
            grid.deleteLater()
            shortcut.deleteLater()
            proxy.deleteLater()

    @Slot(QAccordionItem)
    def _on_entered_section(self, section: QAccordionItem) -> None:
        """Handles the entered section event in the accordion.

        Args:
            section (QAccordionItem): The section that was entered.
        """
        if section in self.accordion().items():
            shortcut = self._shortcuts_container.findChild(QToolButton, section.objectName())
            if section.header().isExpanded():
                shortcut.setChecked(True)

    @Slot(QModelIndex)
    def _on_hover_emoji(self, index: QModelIndex) -> None:
        """Updates the preview label when an emoji is hovered.

        Args:
            index (QModelIndex): Index of the hovered emoji.
        """
        item = self._model.itemFromProxyIndex(index)
        if not item:
            return
        metrics = QFontMetrics(self._aliases_emoji_label.font())
        alias = item.data(QEmojiDataRole.AliasRole)
        elided_alias = metrics.elidedText(alias, Qt.TextElideMode.ElideRight, self._aliases_emoji_label.width())
        self._aliases_emoji_label.setText(elided_alias)
        self._emoji_on_label = item.data(Qt.ItemDataRole.EditRole)
        self._redraw_alias_emoji()

    @Slot(QModelIndex)
    def _on_emoji_clicked(self, proxy_index: QModelIndex) -> None:
        """Handles emoji selection.

        Args:
            proxy_index (QModelIndex): Index of the clicked emoji.
        """
        item = self._model.itemFromProxyIndex(proxy_index)
        if not item:
            return
        self._model.setRecentEmoji(item, True)
        self.picked.emit(item.data(Qt.ItemDataRole.EditRole))

    @Slot(QEmojiGrid, QPoint)
    def _on_context_menu(self, grid: QEmojiGrid, position: QPoint) -> None:
        """Handles the context menu for an emoji.

        Args:
            grid (QEmojiGrid): The grid where the event occurred.
            position (QPoint): Pixel position.
        """
        proxy_index = grid.indexAt(position)
        item = self._model.itemFromProxyIndex(proxy_index)

        if not item:
            return

        menu = QMenu(grid)

        if self.categoryModel().categoryItem(EmojiCategory.Favorites):
            item_favorited = item.data(QEmojiDataRole.FavoriteRole)

            if item_favorited:
                action = menu.addAction(self.tr("Unfavorite"))
                action.triggered.connect(lambda: self._model.setFavoriteEmoji(item, False))
            else:
                action = menu.addAction(self.tr("Favorite"))
                action.triggered.connect(lambda: self._model.setFavoriteEmoji(item, True))

        copy_alias_action = menu.addAction(self.tr("Copy alias"))
        copy_alias_action.triggered.connect(lambda: QApplication.clipboard().setText(item.alias()))

        menu.exec(grid.mapToGlobal(position))

    @Slot(QAccordionItem)
    def _on_shortcut_clicked(self, section: QAccordionItem) -> None:
        """Scrolls the accordion to the selected category section.

        Args:
            section (QAccordionItem): The section to scroll to.
        """
        for section_ in self.accordion().items():
            section_.setExpanded(section_ == section)
        QApplication.processEvents()
        self._accordion.scrollToItem(section)
        
    @Slot()
    def _on_filter_emojis(self) -> None:
        """Filters the emojis across all categories based on the search text."""
        text = self._search_line_edit.text()

        for section in self.accordion().items():
            grid: QEmojiGrid = section.content()
            proxy: QEmojiSortFilterProxyModel = grid.model()
            proxy.setFilterFixedString(text)
            section.setVisible(proxy.rowCount() != 0 or not text)

    @Slot()
    def _on_clear_emoji_preview(self) -> None:
        """Clears the emoji preview area."""
        self._emoji_on_label = None
        self._emoji_label.clear()
        self.__current_alias = ""
        self._aliases_emoji_label.clear()
        
    @Slot(int)
    def _on_emoji_size_changed(self, size: int) -> None:
        """Updates the grid size when the emoji size changes.

        Args:
            size (int): The new emoji size.
        """
        size_obj = QSize(size, size)
        for section in self.accordion().items():
            grid: QEmojiGrid = section.content()
            grid.setGridSize(size_obj)
            grid.setIconSize(size_obj)

    def _redraw_skintones(self) -> None:
        """Updates the skin tone selector icons."""
        emoji_pixmap_getter = self._delegate.emojiPixmapGetter()

        for index, emoji in enumerate(self._skin_tone_selector_emojis.values()):
            if emoji_pixmap_getter:
                size = self._skin_tone_selector.iconSize().width()
                dpr = self.devicePixelRatio()
                self._skin_tone_selector.setItemIcon(index, emoji_pixmap_getter(emoji, 0, size, dpr))
            else:
                self._skin_tone_selector.setItemIcon(index, None)
                self._skin_tone_selector.setItemText(index, emoji)

    def _redraw_alias_emoji(self) -> None:
        """Updates the emoji preview label pixmap."""
        if self._emoji_on_label:
            emoji_pixmap_getter = self._delegate.emojiPixmapGetter()

            if emoji_pixmap_getter:
                pixmap = emoji_pixmap_getter(self._emoji_on_label, 0, self._delegate.emojiSize(), self.devicePixelRatio())
                self._emoji_label.setPixmap(pixmap)
            else:
                self._emoji_label.setText(self._emoji_on_label)

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

    def _create_grid(self) -> QEmojiGrid:
        """Creates an emoji grid.

        Returns:
            QEmojiGrid: The created grid.
        """
        return QEmojiGrid(self, self._delegate)

    # --- Public API (camelCase) ---

    def translateUI(self) -> None:
        """Translates the UI components."""
        self._search_line_edit.setPlaceholderText(self.tr("Search emoji..."))

        for section in self.accordion().items():
            category = section.objectName()
            section.setTitle(QApplication.translate("EmojiCategory", category))

    def resetPicker(self) -> None:
        """Resets the picker state."""
        self._search_line_edit.clear()
        self._accordion.resetScroll()

    def accordion(self) -> QAccordion:
        """Returns the accordion widget.

        Returns:
            QAccordion: The accordion.
        """
        return self._accordion

    def setModel(self, model: QEmojiModel) -> None:
        """Sets the emoji model.

        Args:
            model (QEmojiModel): The new emoji model.
        """
        if model != self._model:
            self._model = model
            for section in self.accordion().items():
                grid: QEmojiGrid = section.content()
                proxy: QEmojiSortFilterProxyModel = grid.model()
                proxy.setSourceModel(model)

    def model(self) -> QEmojiModel:
        """Returns the base emoji model.

        Returns:
            QEmojiModel: The emoji model.
        """
        return self._model
        
    def categoryModel(self) -> QEmojiCategoryModel:
        """Returns the category model.

        Returns:
            QEmojiCategoryModel: The category model.
        """
        return self._category_model

    def delegate(self) -> QEmojiDelegate:
        """Returns the emoji delegate.

        Returns:
            QEmojiDelegate: The emoji delegate.
        """
        return self._delegate

    def setDelegate(self, delegate: QEmojiDelegate) -> None:
        """Sets the emoji delegate.

        Args:
            delegate (QEmojiDelegate): The new emoji delegate.
        """
        if self._delegate == delegate:
            return

        if self._delegate:
            self._delegate.emojiSizeChanged.disconnect(self._on_emoji_size_changed)
            self._delegate.emojiPixmapGetterChanged.disconnect(self._on_emoji_pixmap_getter_changed)
            self._delegate.emojiFontChanged.disconnect(self._on_emoji_font_changed)

        self._delegate = delegate

        if self._delegate:
            if self._delegate.parent() is None:
                self._delegate.setParent(self)

            self._delegate.emojiSizeChanged.connect(self._on_emoji_size_changed)
            self._delegate.emojiPixmapGetterChanged.connect(self._on_emoji_pixmap_getter_changed)
            self._delegate.emojiFontChanged.connect(self._on_emoji_font_changed)

            for section in self.accordion().items():
                grid: QEmojiGrid = section.content()
                grid.setItemDelegate(self._delegate)

            self._on_emoji_font_changed(self._delegate.emojiFont())
            self._on_emoji_size_changed(self._delegate.emojiSize())
            self._on_emoji_pixmap_getter_changed()