from PySide6.QtWidgets import QAbstractItemView
from qextrawidgets.core.utils import QIconGenerator
from qextrawidgets.widgets.views.grouped_icon_view import QGroupedIconView
from qextrawidgets.gui.items.emoji_item import EmojiSkinTone
import typing
from functools import partial

from PySide6.QtCore import (
    QSize,
    QModelIndex,
    Signal,
    QPoint,
    Qt,
    QTimer,
    Slot,
    QPersistentModelIndex,
)
from PySide6.QtGui import QFont, QIcon, QFontMetrics, QPixmap
from PySide6.QtWidgets import (
    QLineEdit,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    QButtonGroup,
    QMenu,
    QToolButton,
    QApplication,
)

from qextrawidgets.widgets.delegates import QGroupedIconDelegate
from qextrawidgets.core.utils.twemoji_image_provider import QTwemojiImageProvider
from qextrawidgets.gui.items import QEmojiCategoryItem
from qextrawidgets.gui.models.emoji_picker_model import EmojiCategory, QEmojiPickerModel
from qextrawidgets.gui.proxys import QEmojiPickerProxyModel
from qextrawidgets.gui.items import QEmojiItem
from qextrawidgets.widgets.inputs.icon_combo_box import QIconComboBox
from qextrawidgets.widgets.inputs.search_line_edit import QSearchLineEdit


class QEmojiPicker(QWidget):
    """A comprehensive emoji picker widget.

    Features categories, search, skin tone selection, and recent/favorite emojis.

    Signals:
        picked (str): Emitted when an emoji is selected.
    """

    picked = Signal(QEmojiItem)

    def __init__(
        self,
        model: typing.Optional[QEmojiPickerModel] = None,
        emoji_pixmap_getter: typing.Union[
            str, QFont, typing.Callable[[str], QPixmap]
        ] = partial(QTwemojiImageProvider.getPixmap, margin=0, size=128),
        emoji_label_size: QSize = QSize(32, 32),
    ) -> None:
        """Initializes the emoji picker.

        Args:
            model (QEmojiPickerModel, optional): Custom emoji model. Defaults to None.
            emoji_pixmap_getter (Union[str, QFont, Callable[[str], QPixmap]], optional):
                Method or font to generate emoji pixmaps. Defaults to EmojiImageProvider.getPixmap.
            emoji_label_size (QSize, optional): Size of the preview emoji label. Defaults to QSize(32, 32).
        """
        super().__init__()

        self._skin_tone_selector_emojis = {
            EmojiSkinTone.Default: "👏",
            EmojiSkinTone.Light: "👏🏻",
            EmojiSkinTone.MediumLight: "👏🏼",
            EmojiSkinTone.Medium: "👏🏽",
            EmojiSkinTone.MediumDark: "👏🏾",
            EmojiSkinTone.Dark: "👏🏿",
        }

        if model:
            self._model = model
        else:
            self._model = QEmojiPickerModel()

        self._proxy = QEmojiPickerProxyModel()
        self._proxy.setSourceModel(self._model)

        self._search_line_edit = self._create_search_line_edit()

        self._grouped_icon_view = QGroupedIconView(self, QSize(40, 40), 5)
        self._grouped_icon_view.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self._grouped_icon_view.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )
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

        self._emoji_pixmap_getter: typing.Callable[[str], QPixmap]
        self.setEmojiPixmapGetter(emoji_pixmap_getter)
        self.setContentsMargins(5, 5, 5, 5)

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
        self._model.categoryRemoved.connect(self._on_categories_removed)

        self._grouped_icon_view.itemEntered.connect(self._on_mouse_entered_emoji)
        self._grouped_icon_view.itemExited.connect(self._on_mouse_exited_emoji)
        self._grouped_icon_view.itemClicked.connect(self._on_item_clicked)
        self._grouped_icon_view.customContextMenuRequested.connect(
            self._on_context_menu
        )

        self._skin_tone_selector.currentDataChanged.connect(self._on_set_skin_tone)

        delegate: QGroupedIconDelegate = self._grouped_icon_view.itemDelegate()
        delegate.requestImage.connect(self._on_request_image)

        self._model.skinToneChanged.connect(self._on_skin_tone_changed)

    @Slot(QModelIndex)
    def _on_skin_tone_changed(self, source_index: QModelIndex) -> None:
        """Handles skin tone changes from the model.

        Args:
            source_index (QModelIndex): The index in the source model that changed.
        """
        proxy_index = self._proxy.mapFromSource(source_index)
        delegate: QGroupedIconDelegate = self._grouped_icon_view.itemDelegate()
        delegate.forceReload(proxy_index)

    @Slot(str)
    def _on_set_skin_tone(self, skin_tone: str) -> None:
        """Updates the skin tone of the emojis.

        Args:
            skin_tone (str): Skin tone modifier.
        """
        self._model.setSkinTone(skin_tone)

    @Slot(QModelIndex)
    def _on_item_clicked(self, proxy_index: QModelIndex) -> None:
        """Handles clicks on emoji items.

        Args:
            proxy_index (QModelIndex): The index in the proxy model that was clicked.
        """
        source_index = self._proxy.mapToSource(proxy_index)
        item = self._model.itemFromIndex(source_index)

        if not isinstance(item, QEmojiItem):
            return

        self.picked.emit(item)

        recent_category_item = self._model.findCategory(EmojiCategory.Recents)

        if recent_category_item:
            self._model.addEmoji(EmojiCategory.Recents, item.emojiChar())

    @Slot(QPoint)
    def _on_context_menu(self, position: QPoint) -> None:
        """Handles the context menu for an emoji.

        Args:
            position (QPoint): Pixel position where the context menu was requested.
        """
        proxy_index = self._grouped_icon_view.indexAt(position)
        source_index = self._proxy.mapToSource(proxy_index)
        item = self._model.itemFromIndex(source_index)

        menu = QMenu(self._grouped_icon_view)

        if isinstance(item, QEmojiCategoryItem):
            collapse_all_action = menu.addAction(self.tr("Collapse all"))
            collapse_all_action.triggered.connect(self._grouped_icon_view.collapseAll)
            expand_all_action = menu.addAction(self.tr("Expand all"))
            expand_all_action.triggered.connect(self._grouped_icon_view.expandAll)

        elif isinstance(item, QEmojiItem):
            emoji_char = item.data(QEmojiItem.QEmojiDataRole.EmojiRole)

            # Check if emoji exists in favorites using helper method
            favorite_item = self._model.findEmojiInCategoryByName(
                EmojiCategory.Favorites, emoji_char
            )

            if favorite_item:
                action = menu.addAction(self.tr("Unfavorite"))
                action.triggered.connect(
                    lambda: self._model.removeEmoji(EmojiCategory.Favorites, emoji_char)
                )
            else:
                action = menu.addAction(self.tr("Favorite"))
                # We use item.emojiChar() here because addEmoji expects an EmojiChar object
                action.triggered.connect(
                    lambda: self._model.addEmoji(
                        EmojiCategory.Favorites, item.emojiChar()
                    )
                )

            copy_alias_action = menu.addAction(self.tr("Copy alias"))
            clipboard = QApplication.clipboard()
            alias = item.firstAlias()
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
        if not persistent_index.isValid():
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
        if isinstance(item, QEmojiItem):
            # Generate the pixmap
            pixmap = self.emojiPixmapGetter()(item.emoji())

            # Debug: Ensure the pixmap was generated
            if pixmap.isNull():
                print(f"ALERT: Null pixmap generated for {item.emoji()}")

            # Set the icon (This triggers dataChanged in model -> proxy -> view)
            item.setIcon(pixmap)

    @Slot(QEmojiCategoryItem)
    def _on_categories_inserted(self, category_item: QEmojiCategoryItem) -> None:
        """Handles the insertion of categories into the model.

        Args:
            category_item (QEmojiCategoryItem): The inserted category item.
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

    @Slot(QEmojiCategoryItem)
    def _on_categories_removed(self, category_item: QEmojiCategoryItem) -> None:
        category = category_item.category()
        button = self._shortcuts_container.findChild(QToolButton, category)

        if button:
            self._shortcuts_layout.removeWidget(button)
            self._shortcuts_group.removeButton(button)
            button.deleteLater()

    @Slot(QModelIndex)
    def _on_mouse_entered_emoji(self, index: QModelIndex) -> None:
        """Handles mouse entry events on emoji items to show preview.

        Args:
            index (QModelIndex): The index of the item under the mouse.
        """
        source_index = self._proxy.mapToSource(index)
        item = self._model.itemFromIndex(source_index)
        if isinstance(item, QEmojiItem):
            self._emoji_on_label = item.emoji()
            self._paint_emoji_on_label()
            metrics = QFontMetrics(self._aliases_emoji_label.font())
            aliases_text = item.aliasesText()
            elided_alias = metrics.elidedText(
                aliases_text,
                Qt.TextElideMode.ElideRight,
                self._aliases_emoji_label.width(),
            )
            self._aliases_emoji_label.setText(elided_alias)

    @Slot(QModelIndex)
    def _on_shortcut_clicked(self, source_index: QModelIndex) -> None:
        """Scrolls the view to the selected category section.

        Args:
            source_index (QModelIndex): The index of the category in the source model.
        """
        proxy_index = self._proxy.mapFromSource(source_index)
        self._grouped_icon_view.scrollTo(proxy_index)
        self._grouped_icon_view.setExpanded(proxy_index, True)

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

    def _paint_emoji_on_label(self) -> None:
        """Updates the preview label with the current emoji pixmap."""
        if self._emoji_on_label:
            pixmap = self.emojiPixmapGetter()(self._emoji_on_label)
            self._emoji_label.setPixmap(pixmap)

    def _paint_skintones(self) -> None:
        """Updates the skin tone selector icons."""
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

    def setEmojiPixmapGetter(
        self,
        emoji_pixmap_getter: typing.Union[str, QFont, typing.Callable[[str], QPixmap]],
    ) -> None:
        """Sets the strategy for retrieving emoji pixmaps.

        Args:
            emoji_pixmap_getter (Union[str, QFont, Callable[[str], QPixmap]]):
                Can be a font family name (str), a QFont object, or a callable that takes an emoji string
                and returns a QPixmap.
        """
        if isinstance(emoji_pixmap_getter, str):
            font_family = emoji_pixmap_getter
        elif isinstance(emoji_pixmap_getter, QFont):
            font_family = emoji_pixmap_getter.family()
        else:
            font_family = None

        if font_family:
            emoji_font = QFont()
            emoji_font.setFamily(font_family)
            self._emoji_pixmap_getter = partial(
                QIconGenerator.charToPixmap,
                font=emoji_font,
                target_size=QSize(100, 100),
            )
        else:
            self._emoji_pixmap_getter = typing.cast(
                typing.Callable[[str], QPixmap], emoji_pixmap_getter
            )

        self._paint_emoji_on_label()
        self._paint_skintones()

        delegate = self.delegate()
        delegate.forceReloadAll()

    def emojiPixmapGetter(self) -> typing.Callable[[str], QPixmap]:
        """Returns the current emoji pixmap getter function.

        Returns:
            Callable[[str], QPixmap]: A function that takes an emoji string and returns a QPixmap.
        """
        return self._emoji_pixmap_getter

    def delegate(self) -> QGroupedIconDelegate:
        """Returns the item delegate used by the view."""
        return self._grouped_icon_view.itemDelegate()

    def view(self) -> QGroupedIconView:
        """Returns the internal grouped icon view."""
        return self._grouped_icon_view

    def model(self) -> QEmojiPickerModel:
        """Returns the emoji picker model."""
        return self._model
