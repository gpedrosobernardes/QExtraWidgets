import logging
import time
import typing

from PySide6.QtCore import QSize, QTimer, Slot, QPoint, QPersistentModelIndex, QModelIndex, Signal
from PySide6.QtGui import Qt, QFont, QPixmap, QIcon, QFontMetrics
from PySide6.QtWidgets import QWidget, QAbstractItemView, QButtonGroup, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, \
    QMenu, QApplication, QToolButton

from qextrawidgets.gui.items import QIconCategoryItem
from qextrawidgets.gui.items.icon_item import QIconItem
from qextrawidgets.gui.models.icon_picker_model import QIconPickerModel
from qextrawidgets.gui.proxys.icon_picker_proxy import QIconPickerProxyModel
from qextrawidgets.widgets.delegates import QGroupedIconDelegate
from qextrawidgets.widgets.inputs import QIconComboBox, QSearchLineEdit
from qextrawidgets.widgets.views import QGroupedIconView


class QIconPicker(QWidget):
    """A generic icon picker widget.

    Features categories, search, recent and favorites.

    Signals:
        picked: Emitted when a QIcon item is clicked.
    """

    picked = Signal(QIconItem)

    def __init__(self,
                 parent=None,
                 model: typing.Optional[QIconPickerModel] = None,
                 icon_label_size: int = 32,
                 icon_pixmap_getter: typing.Callable[[QIconItem], QPixmap] = None,
                 alias_format: str = "{alias}") -> None:
        """
        Initialize QIconPicker widget.
        Setup widgets, layout and models.

        Args:
            parent: Parent widget.
            model: Optional QIconPickerModel instance.
            icon_label_size: Size of the icon label.
            icon_pixmap_getter: Optional function that takes an icon item and returns the pixmap.
            alias_format: Format of the alias icon label.
        """
        super().__init__(parent)

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(200)

        self._proxy = QIconPickerProxyModel()

        self._icon_on_label = None
        self._model = None

        self._init_view(icon_label_size)
        self._setup_layout()
        self._setup_connections()
        self._init_models(model)

        if icon_pixmap_getter is None:
            self._icon_pixmap_getter = None
        else:
            self.setIconPixmapGetter(icon_pixmap_getter)

        self.setAliasFormat(alias_format)

    def _init_models(self, model: typing.Optional[QIconPickerModel]):
        """
        Initialize the icon picker model.

        Args:
            model: Optional QIconPickerModel instance.
        """
        self._grouped_icon_view.setModel(self._proxy)

        if model is None:
            model = QIconPickerModel()
        self.setModel(model)

    def _init_view(self, icon_label_size: int) -> None:
        """
        Initialize the internal widgets of the view.

        Args:
            icon_label_size: Size of the icon label.
        """
        self._search_line_edit = self._create_search_line_edit()

        self._color_modifier_selector = QIconComboBox()

        self._grouped_icon_view = QGroupedIconView(self, QSize(40, 40), 5)
        self._grouped_icon_view.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self._grouped_icon_view.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )

        self._shortcuts_container = QWidget()
        self._shortcuts_container.setFixedHeight(40)  # Fixed height for the bar

        self._shortcuts_group = QButtonGroup(self)
        self._shortcuts_group.setExclusive(True)

        self._icon_label = QLabel()
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setScaledContents(True)
        self.setIconLabelSize(icon_label_size)

        self._aliases_icon_label = self._create_icon_label()

        self.setContentsMargins(10, 10, 10, 10)

    # Private methods
    @staticmethod
    def _create_icon_label() -> QLabel:
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

    def _setup_layout(self) -> None:
        """Sets up the initial layout of the widget."""
        self._shortcuts_layout = QHBoxLayout(self._shortcuts_container)
        self._shortcuts_layout.setContentsMargins(5, 0, 5, 0)
        self._shortcuts_layout.setSpacing(2)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self._search_line_edit, True)
        header_layout.addWidget(self._color_modifier_selector)

        content_layout = QHBoxLayout()
        content_layout.addWidget(self._icon_label)
        content_layout.addWidget(self._aliases_icon_label, True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self._shortcuts_container)
        main_layout.addWidget(self._grouped_icon_view)
        main_layout.addLayout(content_layout)

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

    def _setup_connections(self) -> None:
        """Sets up signals and slots connections."""
        self._search_timer.timeout.connect(self._on_filter_emojis)
        self._search_line_edit.textChanged.connect(lambda: self._search_timer.start())

        self._grouped_icon_view.itemEntered.connect(self._on_mouse_entered_emoji)
        self._grouped_icon_view.itemExited.connect(self._on_mouse_exited_emoji)
        self._grouped_icon_view.itemClicked.connect(self._on_item_clicked)
        self._grouped_icon_view.customContextMenuRequested.connect(
            self._on_context_menu
        )

        self._color_modifier_selector.currentDataChanged.connect(self._on_set_color_modifier)

        delegate: QGroupedIconDelegate = self._grouped_icon_view.itemDelegate()
        delegate.requestImage.connect(self._on_request_image)

    @Slot(QModelIndex)
    def _on_color_modifier_changed(self, index: QModelIndex) -> None:
        """Handles skin tone changes from the model.

        Args:
            index (QModelIndex): The index in the source model that changed.
        """
        logging.debug("Requesting image again for {}".format(index.data(Qt.ItemDataRole.EditRole)))
        proxy_index = self._proxy.mapFromSource(index)
        delegate: QGroupedIconDelegate = self._grouped_icon_view.itemDelegate()
        delegate.forceReload(proxy_index)

    @Slot(QIconItem)
    def _on_set_color_modifier(self, icon_item: QIconItem) -> None:
        """Updates the skin tone of the emojis.

        Args:
            icon_item (QIconItem): QIconItem instance representing the color_modifier.
        """
        color_modifier = icon_item.data(QIconItem.QIconItemDataRole.ColorModifierRole)
        self.model().setColorModifier(color_modifier)

    # Connections
    @Slot(QPoint)
    def _on_context_menu(self, position: QPoint) -> None:
        """Handles the context menu for an icon.

        Args:
            position (QPoint): Pixel position where the context menu was requested.
        """
        proxy_index = self._grouped_icon_view.indexAt(position)
        source_index = self._proxy.mapToSource(proxy_index)
        item = self._model.itemFromIndex(source_index)

        menu = QMenu(self._grouped_icon_view)

        if isinstance(item, QIconCategoryItem):
            collapse_all_action = menu.addAction(self.tr("Collapse all"))
            collapse_all_action.triggered.connect(self._grouped_icon_view.collapseAll)
            expand_all_action = menu.addAction(self.tr("Expand all"))
            expand_all_action.triggered.connect(self._grouped_icon_view.expandAll)

        elif isinstance(item, QIconItem):
            icon_text = item.data(Qt.ItemDataRole.EditRole)

            # Check if emoji exists in favorites using helper method
            favorite_item = self._model.findIconInCategoryByName(
                QIconPickerModel.BaseCategory.Favorites, icon_text
            )

            if favorite_item:
                action = menu.addAction(self.tr("Unfavorite"))
                action.triggered.connect(
                    lambda: self._model.removeIcon(QIconPickerModel.BaseCategory.Favorites, icon_text)
                )
            else:
                action = menu.addAction(self.tr("Favorite"))
                # We use item.emojiChar() here because addEmoji expects an EmojiChar object
                action.triggered.connect(
                    lambda: self._model.addIcon(QIconPickerModel.BaseCategory.Favorites, item.clone())
                )

            copy_alias_action = menu.addAction(self.tr("Copy alias"))
            clipboard = QApplication.clipboard()
            aliases = item.data(Qt.ItemDataRole.UserRole)

            alias = aliases[0] if aliases else item.data(Qt.ItemDataRole.EditRole)
            copy_alias_action.triggered.connect(lambda: clipboard.setText(alias))
        else:
            return

        menu.exec(self._grouped_icon_view.mapToGlobal(position))

    @Slot(QPersistentModelIndex)
    def _on_request_image(self, persistent_index: QPersistentModelIndex) -> None:
        """Loads the emoji image when requested by the delegate.

        Args:
            persistent_index (QPersistentModelIndex): The persistent index of the item needing an image.
        """
        start = time.perf_counter()

        if not persistent_index.isValid():
            return

        icon_pixmap_getter = self.iconPixmapGetter()

        if not icon_pixmap_getter:
            return

        # 1. Explicitly convert to QModelIndex
        # Note: QModelIndex constructor does not accept QPersistentModelIndex directly in PySide6
        proxy_index = persistent_index.model().index(
            persistent_index.row(), persistent_index.column(), persistent_index.parent()
        )

        if not proxy_index.isValid():
            return

        # 2. Map from Proxy to Source Model
        source_index = self._proxy.mapToSource(proxy_index)

        if not source_index.isValid():
            return

        # 3. Fetch the item and set the image
        item = self._model.itemFromIndex(source_index)
        if isinstance(item, QIconItem):
            # Generate the pixmap
            pixmap = icon_pixmap_getter(item)

            # Debug: Ensure the pixmap was generated
            if pixmap.isNull():
                logging.warning(f"Null pixmap generated for {item.data(Qt.ItemDataRole.EditRole)}")

            # Set the icon (This triggers dataChanged in model -> proxy -> view)
            item.setIcon(pixmap)

        end = time.perf_counter()
        logging.debug(f"Requested image for {item.data(Qt.ItemDataRole.EditRole)} in {end - start:.6f} seconds")

    def _paint_emoji_on_label(self) -> None:
        """Updates the preview label with the current emoji pixmap."""
        icon_pixmap_getter = self.iconPixmapGetter()
        if self._icon_on_label and icon_pixmap_getter:
            pixmap = icon_pixmap_getter(self._icon_on_label)
            self._icon_label.setPixmap(pixmap)

    def _paint_skintones(self) -> None:
        """Updates the skin tone selector icons."""
        for index in range(self._color_modifier_selector.count()):
            icon_item = self._color_modifier_selector.itemData(index)
            icon = self.iconPixmapGetter()(icon_item)
            if icon:
                self._color_modifier_selector.setItemIcon(index, icon)

    @Slot(QModelIndex)
    def _on_shortcut_clicked(self, source_index: QModelIndex) -> None:
        """Scrolls the view to the selected category section.

        Args:
            source_index (QModelIndex): The index of the category in the source model.
        """
        proxy_index = self._proxy.mapFromSource(source_index)
        self._grouped_icon_view.scrollTo(proxy_index)
        self._grouped_icon_view.setExpanded(QPersistentModelIndex(proxy_index), True)

    @Slot(QIconCategoryItem)
    def _on_categories_inserted(self, category_item: QIconCategoryItem) -> None:
        """Handles the insertion of categories into the model.

        Args:
            category_item (QIconCategoryItem): The inserted category item.
        """
        category = category_item.text()
        icon = category_item.icon()

        shortcut = self._create_shortcut_button(category, icon)
        shortcut.setObjectName(category)
        shortcut.clicked.connect(
            lambda: self._on_shortcut_clicked(category_item.index())
        )

        self._shortcuts_layout.addWidget(shortcut)
        self._shortcuts_group.addButton(shortcut)

    @Slot(QIconCategoryItem)
    def _on_categories_removed(self, category_item: QIconCategoryItem) -> None:
        """Handles the removal of categories into the model.

        Args:
            category_item (QIconCategoryItem): The removed category item.
        """
        category = category_item.category()
        button = self._shortcuts_container.findChild(QToolButton, category)

        if button:
            self._shortcuts_layout.removeWidget(button)
            self._shortcuts_group.removeButton(button)
            button.deleteLater()

    @Slot()
    def _on_model_reset(self):
        """Handles the reset of the model."""
        for button in self._shortcuts_group.buttons():
            self._shortcuts_layout.removeWidget(button)
            self._shortcuts_group.removeButton(button)
            button.deleteLater()

        model = self.model()
        for row in range(model.rowCount()):
            item = model.item(row)
            if isinstance(item, QIconCategoryItem):
                self._on_categories_inserted(item)

    @Slot(QModelIndex)
    def _on_mouse_entered_emoji(self, index: QModelIndex) -> None:
        """Handles mouse entry events on emoji items to show preview.

        Args:
            index (QModelIndex): The index of the item under the mouse.
        """
        source_index = self._proxy.mapToSource(index)
        item = self._model.itemFromIndex(source_index)
        if isinstance(item, QIconItem):
            self._icon_on_label = item
            self._paint_emoji_on_label()

            aliases = item.data(Qt.ItemDataRole.UserRole) or [item.data(Qt.ItemDataRole.EditRole)]
            aliases_text = " ".join(self._alias_format.format(alias=alias) for alias in aliases)

            metrics = QFontMetrics(self._aliases_icon_label.font())
            elided_alias = metrics.elidedText(
                aliases_text,
                Qt.TextElideMode.ElideRight,
                self._aliases_icon_label.width(),
            )
            self._aliases_icon_label.setText(elided_alias)

    @Slot()
    def _on_mouse_exited_emoji(self) -> None:
        """Clears the emoji preview area."""
        self._icon_label.clear()
        self._aliases_icon_label.clear()
        self._emoji_on_label = None

    @Slot(QModelIndex)
    def _on_item_clicked(self, proxy_index: QModelIndex) -> None:
        """Handles clicks on emoji items.

        Args:
            proxy_index (QModelIndex): The index in the proxy model that was clicked.
        """
        source_index = self._proxy.mapToSource(proxy_index)
        item = self._model.itemFromIndex(source_index)

        if not isinstance(item, QIconItem):
            return

        self.picked.emit(item)

        recent_category_item = self._model.findCategory(QIconPickerModel.BaseCategory.Recents)

        if recent_category_item:
            self._model.addIcon(QIconPickerModel.BaseCategory.Recents, item.clone())

    @Slot()
    def _on_filter_emojis(self) -> None:
        """Filters the emojis across all categories based on the search text."""
        text = self._search_line_edit.text()
        self._proxy.setFilterFixedString(text)

    # Public methods
    def addColorOption(self, data: QIconItem):
        """
        Adds a color option to the color selector in the icon picker.

        Args:
            data: QIconItem instance.
        """
        icon_pixmap_getter = self.iconPixmapGetter()
        if icon_pixmap_getter:
            icon = icon_pixmap_getter(data)
        else:
            icon = QIcon()
        self._color_modifier_selector.addItem(icon=icon, data=data)

    def setIconPixmapGetter(
        self,
        icon_pixmap_getter: typing.Callable[[QIconItem], QPixmap],
    ) -> None:
        """Sets the strategy for retrieving icon pixmaps.

        Args:
            icon_pixmap_getter (Callable[[QIconItem], QPixmap]):
                Can be a font family name (str), a QFont object, or a callable that takes an emoji string
                and returns a QPixmap.
        """

        self._icon_pixmap_getter = icon_pixmap_getter

        self._paint_emoji_on_label()
        self._paint_skintones()

        delegate = self.delegate()
        delegate.forceReloadAll()

    def iconPixmapGetter(self) -> typing.Callable[[QIconItem], QPixmap]:
        """Returns the current emoji pixmap getter function.

        Returns:
            Callable[[QIconItem], QPixmap]: A function that takes an emoji string and returns a QPixmap.
        """
        return self._icon_pixmap_getter

    def setModel(self, model: QIconPickerModel):
        """
        Setter for icon picker model.

        Args:
            model(QIconPickerModel): The icon picker model.
        """
        if model != self._model:
            if self._model:
                self._model.categoryInserted.disconnect(self._on_categories_inserted)
                self._model.categoryRemoved.disconnect(self._on_categories_removed)
                self._model.colorChanged.disconnect(self._on_color_modifier_changed)

            self._model = model
            self._proxy.setSourceModel(self._model)

            self._model.categoryInserted.connect(self._on_categories_inserted)
            self._model.categoryRemoved.connect(self._on_categories_removed)
            self._model.colorChanged.connect(self._on_color_modifier_changed)

            self._on_model_reset()

    def model(self) -> QIconPickerModel:
        """Returns the emoji picker model."""
        return self._model

    def setIconLabelSize(self, size: int):
        """
        Setter for icon label size.

        Args:
            size(int): The size of the icon label
        """
        self._icon_label.setFixedSize(QSize(size, size))

    def setAliasFormat(self, alias_format: str):
        """
        Setter for alias format.

        Args:
            alias_format: Alias format.
        """
        self._alias_format = alias_format

    def translateUI(self) -> None:
        """Translates the UI components."""
        self._search_line_edit.setPlaceholderText(self.tr("Search emoji..."))

    def resetPicker(self) -> None:
        """Resets the picker state."""
        self._search_line_edit.clear()

    def delegate(self) -> QGroupedIconDelegate:
        """Returns the item delegate used by the view."""
        return self._grouped_icon_view.itemDelegate()

    def view(self) -> QGroupedIconView:
        """Returns the internal grouped icon view."""
        return self._grouped_icon_view
