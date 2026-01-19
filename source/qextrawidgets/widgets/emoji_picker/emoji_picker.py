import typing
from enum import Enum

from PySide6.QtCore import QSize, QT_TR_NOOP, QModelIndex, Signal, QPoint, Qt, QSizeF
from PySide6.QtGui import QFont, QIcon, QStandardItem, QFontMetrics, QPixmap
from PySide6.QtWidgets import (QLineEdit, QHBoxLayout, QLabel, QVBoxLayout,
                               QWidget, QApplication, QButtonGroup, QMenu, QToolButton)
from emoji_data_python import emoji_data, EmojiChar

from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.utils import QEmojiFonts, get_max_pixel_size
from qextrawidgets.widgets.accordion import QAccordion
from qextrawidgets.widgets.accordion_item import QAccordionItem
from qextrawidgets.widgets.emoji_picker.emoji_grid import QEmojiGrid
from qextrawidgets.widgets.emoji_picker.emoji_model import QEmojiModel
from qextrawidgets.widgets.emoji_picker.emoji_sort_filter import QEmojiSortFilterProxyModel
from qextrawidgets.widgets.emoji_picker.enums import QEmojiDataRole, EmojiSkinTone
from qextrawidgets.widgets.icon_combo_box import QIconComboBox
from qextrawidgets.widgets.search_line_edit import QSearchLineEdit


class QEmojiPicker(QWidget):
    """A comprehensive emoji picker widget.

    Features categories, search, skin tone selection, and recent/favorite emojis.

    Signals:
        picked (str): Emitted when an emoji is selected.
    """

    picked = Signal(str)

    class EmojiCategory(Enum):
        """Standard emoji categories."""
        Activities = QT_TR_NOOP("Activities")
        FoodAndDrink = QT_TR_NOOP("Food & Drink")
        AnimalsAndNature = QT_TR_NOOP("Animals & Nature")
        PeopleAndBody = QT_TR_NOOP("People & Body")
        Symbols = QT_TR_NOOP("Symbols")
        Flags = QT_TR_NOOP("Flags")
        TravelAndPlaces = QT_TR_NOOP("Travel & Places")
        Objects = QT_TR_NOOP("Objects")
        SmileysAndEmotion = QT_TR_NOOP("Smileys & Emotion")
        Favorites = QT_TR_NOOP("Favorites")
        Recents = QT_TR_NOOP("Recents")

    def __init__(self, favorite_category: bool = True, recent_category: bool = True,
                 emoji_size: int = 40, emoji_font: typing.Optional[str] = None) -> None:
        """Initializes the emoji picker.

        Args:
            favorite_category (bool, optional): Whether to show the favorites category. Defaults to True.
            recent_category (bool, optional): Whether to show the recents category. Defaults to True.
            emoji_size (int, optional): Size of individual emoji items. Defaults to 40.
            emoji_font (str, optional): Font family to use for emojis. If None, Twemoji is loaded. Defaults to None.
        """
        super().__init__()

        self._icons = {
            self.EmojiCategory.Activities.value: QThemeResponsiveIcon.fromAwesome("fa6s.gamepad", options=[{"scale_factor": 0.9}]),
            self.EmojiCategory.FoodAndDrink.value: QThemeResponsiveIcon.fromAwesome("fa6s.bowl-food"),
            self.EmojiCategory.AnimalsAndNature.value: QThemeResponsiveIcon.fromAwesome("fa6s.leaf"),
            self.EmojiCategory.PeopleAndBody.value: QThemeResponsiveIcon.fromAwesome("fa6s.user"),
            self.EmojiCategory.Symbols.value: QThemeResponsiveIcon.fromAwesome("fa6s.heart"),
            self.EmojiCategory.Flags.value: QThemeResponsiveIcon.fromAwesome("fa6s.flag"),
            self.EmojiCategory.TravelAndPlaces.value: QThemeResponsiveIcon.fromAwesome("fa6s.bicycle", options=[{"scale_factor": 0.9}]),
            self.EmojiCategory.Objects.value: QThemeResponsiveIcon.fromAwesome("fa6s.lightbulb"),
            self.EmojiCategory.SmileysAndEmotion.value: QThemeResponsiveIcon.fromAwesome("fa6s.face-smile"),
            self.EmojiCategory.Favorites.value: QThemeResponsiveIcon.fromAwesome("fa6s.star"),
            self.EmojiCategory.Recents.value: QThemeResponsiveIcon.fromAwesome("fa6s.clock-rotate-left")
        }

        self._skin_tone_selector_emojis = {
            EmojiSkinTone.Default: "👏",
            EmojiSkinTone.Light: "👏🏻",
            EmojiSkinTone.MediumLight: "👏🏼",
            EmojiSkinTone.Medium: "👏🏽",
            EmojiSkinTone.MediumDark: "👏🏾",
            EmojiSkinTone.Dark: "👏🏿"
        }

        # Private variables
        self.__favorite_category = None
        self.__recent_category = None
        self._emoji_pixmap_getter = None
        self._emoji_on_label = None
        self.__categories_data = {}  # Stores references to grids and layouts
        # Layout inside the scroll area where grids are located

        self.__emoji_size = None
        if emoji_font is None:
            emoji_font = QEmojiFonts.loadTwemojiFont()
        self.__emoji_font = emoji_font
        self.__emoji_delegate = None

        self.__model = QEmojiModel()
        self.__accordion = QAccordion()

        # 1. Search Bar
        self.__search_line_edit = self._create_search_line_edit()
        self.__skin_tone_selector = QIconComboBox()

        for skin_tone, emoji in self._skin_tone_selector_emojis.items():
            self.__skin_tone_selector.addItem(text=emoji, data=skin_tone.value, font=QFont(emoji_font))

        self._shortcuts_container = QWidget()
        self._shortcuts_container.setFixedHeight(40)  # Fixed height for the bar
        self._shortcuts_layout = QHBoxLayout(self._shortcuts_container)
        self._shortcuts_layout.setContentsMargins(5, 0, 5, 0)
        self._shortcuts_layout.setSpacing(2)

        self._shortcuts_group = QButtonGroup(self)
        self._shortcuts_group.setExclusive(True)

        self.__emoji_label = QLabel()
        self.__emoji_label.setFixedSize(QSize(32, 32))
        self.__emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__emoji_label.setScaledContents(True)

        self.__aliases_emoji_label = self._create_emoji_label()
        self.__menu_horizontal_layout = QHBoxLayout()

        self.__setup_connections()

        # Populates categories (Ideally this would be Lazy, called only when needed)
        self.__add_base_categories()

        self.setFavoriteCategory(favorite_category)
        self.setRecentCategory(recent_category)

        self.__accordion.expandAll()

        self.setEmojiSize(emoji_size)
        self.setEmojiFont(emoji_font)

        self.__setup_layout()
        self.translateUI()

    def __setup_layout(self) -> None:
        """Sets up the initial layout of the widget."""
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.__search_line_edit, True)
        header_layout.addWidget(self.__skin_tone_selector)

        content_layout = QHBoxLayout()
        content_layout.addWidget(self.__emoji_label)
        content_layout.addWidget(self.__aliases_emoji_label, True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self._shortcuts_container)
        main_layout.addWidget(self.__accordion)
        main_layout.addLayout(content_layout)

    def translateUI(self) -> None:
        """Translates the UI components."""
        self.__search_line_edit.setPlaceholderText(self.tr("Search emoji..."))

        for category in self.EmojiCategory:
            section = self.section(category.value)
            if section:
                section.setTitle(self.tr(category.value))

    def _get_emoji_icon_size(self) -> int:
        """Returns the icon size based on the emoji size.

        Returns:
            int: The calculated icon size.
        """
        return self.__emoji_size * 0.8

    def _set_skin_tone(self, skin_tone: str) -> None:
        """Updates the skin tone of the emojis.

        Args:
            skin_tone (str): Skin tone modifier.
        """
        self.__model.setSkinTone(skin_tone)

    def __setup_connections(self) -> None:
        """Sets up signals and slots connections."""
        self.__search_line_edit.textChanged.connect(self.__filter_emojis)
        self.__accordion.enteredSection.connect(self.__on_entered_section)
        self.__skin_tone_selector.currentDataChanged.connect(self._set_skin_tone)

    def __on_entered_section(self, section: QAccordionItem) -> None:
        """Handles the entered section event in the accordion.

        Args:
            section (QAccordionItem): The section that was entered.
        """
        sections = self.sections()
        if section in sections:
            shortcut = self.shortcuts()[sections.index(section)]
            if section.header().isExpanded():
                shortcut.setChecked(True)

    def __filter_emojis(self) -> None:
        """Filters the emojis across all categories based on the search text."""
        text = self.__search_line_edit.text()

        for proxy, section in zip(self.proxys(), self.sections()):
            proxy.setFilterFixedString(text)
            section.setVisible(proxy.rowCount() != 0 or not text)

    def __on_hover_emoji(self, index: QModelIndex) -> None:
        """Updates the preview label when an emoji is hovered.

        Args:
            index (QModelIndex): Index of the hovered emoji.
        """
        if not index.isValid():
            return
        item = self.__model.itemFromProxyIndex(index)
        if not item:
            return
        alias = item.data(QEmojiDataRole.AliasRole)
        metrics = QFontMetrics(self.__aliases_emoji_label.font())
        elided_alias = metrics.elidedText(alias, Qt.TextElideMode.ElideRight, self.__aliases_emoji_label.width())
        self.__aliases_emoji_label.setText(elided_alias)
        self._emoji_on_label = item.data(Qt.ItemDataRole.EditRole)
        self._redraw_alias_emoji()

    def __clear_emoji_preview(self) -> None:
        """Clears the emoji preview area."""
        self._emoji_on_label = None
        self.__emoji_label.clear()
        self.__current_alias = ""
        self.__aliases_emoji_label.clear()

    def __on_emoji_clicked(self, proxy_index: QModelIndex) -> None:
        """Handles emoji selection.

        Args:
            proxy_index (QModelIndex): Index of the clicked emoji.
        """
        if not proxy_index.isValid():
            return
        item = self.__model.itemFromProxyIndex(proxy_index)
        if not item:
            return
        item.setData(True, QEmojiDataRole.RecentRole)
        self.picked.emit(item.data(Qt.ItemDataRole.EditRole))

    def __item_from_position(self, grid: QEmojiGrid, position: QPoint) -> typing.Optional[QStandardItem]:
        """Returns the source model item at the given pixel position in the grid.

        Args:
            grid (QEmojiGrid): The emoji grid.
            position (QPoint): Pixel position.

        Returns:
            QStandardItem, optional: The item at the position, or None.
        """
        proxy_index = grid.indexAt(position)
        if not proxy_index.isValid():
            return None
        return self.__model.itemFromProxyIndex(proxy_index)

    def __on_context_menu(self, grid: QEmojiGrid, position: QPoint) -> None:
        """Handles the context menu for an emoji.

        Args:
            grid (QEmojiGrid): The grid where the event occurred.
            position (QPoint): Pixel position.
        """
        item = self.__item_from_position(grid, position)

        if not item:
            return

        menu = QMenu(grid)

        if self.__favorite_category:
            item_favorited = item.data(QEmojiDataRole.FavoriteRole)

            if item_favorited:
                action = menu.addAction(self.tr("Unfavorite"))
                action.triggered.connect(lambda: item.setData(False, QEmojiDataRole.FavoriteRole))
            else:
                action = menu.addAction(self.tr("Favorite"))
                action.triggered.connect(lambda: item.setData(True, QEmojiDataRole.FavoriteRole))

        copy_alias_action = menu.addAction(self.tr("Copy alias"))
        copy_alias_action.triggered.connect(lambda: QApplication.clipboard().setText(item.data(QEmojiDataRole.AliasRole)))

        menu.exec(grid.mapToGlobal(position))

    @staticmethod
    def _get_emoji_skin_tones_dict(emoji: str, skin_variations: typing.Dict[str, EmojiChar]) -> typing.Optional[typing.Dict[EmojiSkinTone, str]]:
        """Maps skin tone modifiers to actual emoji strings.

        Args:
            emoji (str): Base emoji string.
            skin_variations (Dict[str, EmojiChar]): Available skin variations.

        Returns:
            Dict[EmojiSkinTone, str], optional: Dictionary mapping skin tones to emoji strings or None.
        """
        if skin_variations:
            skin_tones = {skin_tone: found_skin_tone.char for skin_tone in list(EmojiSkinTone) if
                          (found_skin_tone := skin_variations.get(skin_tone))}
            if skin_tones:
                skin_tones[EmojiSkinTone.Default] = emoji
            return skin_tones
        return None

    def __add_base_categories(self) -> None:
        """Populates the picker with standard emoji categories."""
        categories = []

        for data in sorted(emoji_data, key=lambda emoji_: emoji_.sort_order):
            if data.has_img_twitter and data.category != "Component":

                if data.category not in categories:
                    categories.append(data.category)
                    self.addCategory(data.category, data.category, self._icons[data.category])

                skin_tones = self._get_emoji_skin_tones_dict(data.char, data.skin_variations)
                self.__model.addEmoji(data.char, " ".join(f":{alias}:" for alias in data.short_names), data.category, skin_tones=skin_tones)

    def _on_shortcut_clicked(self, section: QAccordionItem) -> None:
        """Scrolls the accordion to the selected category section.

        Args:
            section (QAccordionItem): The section to scroll to.
        """
        self.__accordion.collapseAll()
        section.setExpanded(True)
        QApplication.processEvents()
        self.__accordion.scrollToItem(section)

    def _redraw_skintones(self) -> None:
        """Updates the skin tone selector icons."""
        emoji_pixmap_getter = self.emojiPixmapGetter()

        for index, emoji in enumerate(self._skin_tone_selector_emojis.values()):
            if emoji_pixmap_getter:
                size = self.__skin_tone_selector.iconSize().width()
                dpr = self.devicePixelRatio()
                self.__skin_tone_selector.setItemIcon(index, emoji_pixmap_getter(emoji, 0, size, dpr))
            else:
                self.__skin_tone_selector.setItemIcon(index, None)
                self.__skin_tone_selector.setItemText(index, emoji)

    def _redraw_alias_emoji(self) -> None:
        """Updates the emoji preview label pixmap."""
        if self._emoji_on_label:
            emoji_pixmap_getter = self.emojiPixmapGetter()

            if emoji_pixmap_getter:
                pixmap = emoji_pixmap_getter(self._emoji_on_label, 0, self.emojiSize(), self.devicePixelRatio())
                self.__emoji_label.setPixmap(pixmap)
            else:
                self.__emoji_label.setText(self._emoji_on_label)

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
        btn.setAutoRaise(True)  # Visual flat/clean
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
        return QEmojiGrid(self)

    # --- Public API (camelCase) ---

    def resetPicker(self) -> None:
        """Resets the picker state."""
        self.__search_line_edit.clear()
        self.__accordion.resetScroll()

    def addCategory(self, category: str, text: str, icon: QIcon) -> int:
        """Adds a new emoji category at the end.

        Args:
            category (str): Category identifier.
            text (str): Display text.
            icon (QIcon): Category icon.

        Returns:
            int: The index of the added category.
        """
        index = len(self.__categories_data)
        self.insertCategory(category, index, text, icon)
        return index

    def insertCategory(self, category: str, index: int, text: str, icon: QIcon) -> None:
        """Inserts a new emoji category at the specified index.

        Args:
            category (str): Category identifier.
            index (int): Insertion index.
            text (str): Display text.
            icon (QIcon): Category icon.
        """
        # Proxy
        proxy = QEmojiSortFilterProxyModel(self)
        proxy.setCategoryFilter(text)
        proxy.setSourceModel(self.__model)

        # Grid
        grid = self._create_grid()
        grid.setModel(proxy)

        # Category Section
        section = self.__accordion.insertSection(text, grid, index)
        section.setAnimationEnabled(False)

        shortcut = self._create_shortcut_button(text, icon)
        self._shortcuts_layout.insertWidget(index, shortcut)
        self._shortcuts_group.addButton(shortcut)

        # Connections
        shortcut.clicked.connect(lambda: self._on_shortcut_clicked(section))
        grid.entered.connect(self.__on_hover_emoji)
        grid.left.connect(self.__clear_emoji_preview)
        grid.clicked.connect(self.__on_emoji_clicked)
        grid.customContextMenuRequested.connect(lambda pos, g=grid: self.__on_context_menu(g, pos))

        category_data = dict(grid=grid, shortcut=shortcut, section=section, proxy=proxy)
        self.__categories_data[category] = category_data

    def removeCategory(self, category: str) -> None:
        """Removes the specified category from the picker.

        Args:
            category (str): Category identifier.
        """
        data = self.category(category)
        if not data:
            return

        section, shortcut, grid, proxy = data["section"], data["shortcut"], data["grid"], data["proxy"]

        self.__accordion.removeAccordionItem(section)
        self._shortcuts_layout.removeWidget(shortcut)
        self._shortcuts_group.removeButton(shortcut)

        section.deleteLater()
        grid.deleteLater()
        shortcut.deleteLater()
        proxy.deleteLater()

        self.__categories_data.pop(category)

    def accordion(self) -> QAccordion:
        """Returns the accordion widget.

        Returns:
            QAccordion: The accordion.
        """
        return self.__accordion

    def model(self) -> QEmojiModel:
        """Returns the base emoji model.

        Returns:
            QEmojiModel: The emoji model.
        """
        return self.__model

    def category(self, category: typing.Union[str, EmojiCategory]) -> typing.Optional[dict]:
        """Returns the data dictionary for the given category.

        Args:
            category (Union[str, EmojiCategory]): Category identifier.

        Returns:
            dict, optional: Category data or None.
        """
        return self.__categories_data.get(str(category))

    def proxy(self, category: typing.Union[str, EmojiCategory]) -> typing.Optional[QEmojiSortFilterProxyModel]:
        """Returns the proxy model for the given category.

        Args:
            category (Union[str, EmojiCategory]): Category identifier.

        Returns:
            QEmojiSortFilterProxyModel, optional: The proxy model or None.
        """
        data = self.category(category)
        return data["proxy"] if data else None

    def proxys(self) -> typing.List[QEmojiSortFilterProxyModel]:
        """Returns a list of all proxy models.

        Returns:
            List[QEmojiSortFilterProxyModel]: All proxy models.
        """
        return [data["proxy"] for data in self.__categories_data.values()]

    def shortcut(self, category: typing.Union[str, EmojiCategory]) -> typing.Optional[QToolButton]:
        """Returns the shortcut button for the given category.

        Args:
            category (Union[str, EmojiCategory]): Category identifier.

        Returns:
            QToolButton, optional: The shortcut button or None.
        """
        data = self.category(category)
        return data["shortcut"] if data else None

    def shortcuts(self) -> typing.List[QToolButton]:
        """Returns a list of all shortcut buttons.

        Returns:
            List[QToolButton]: All shortcut buttons.
        """
        return [data["shortcut"] for data in self.__categories_data.values()]

    def section(self, category: typing.Union[str, EmojiCategory]) -> typing.Optional[QAccordionItem]:
        """Returns the accordion section for the given category.

        Args:
            category (Union[str, EmojiCategory]): Category identifier.

        Returns:
            QAccordionItem, optional: The section item or None.
        """
        data = self.category(category)
        return data["section"] if data else None

    def sections(self) -> typing.List[QAccordionItem]:
        """Returns a list of all accordion sections.

        Returns:
            List[QAccordionItem]: All sections.
        """
        return [data["section"] for data in self.__categories_data.values()]

    def grid(self, category: typing.Union[str, EmojiCategory]) -> typing.Optional[QEmojiGrid]:
        """Returns the emoji grid for the given category.

        Args:
            category (Union[str, EmojiCategory]): Category identifier.

        Returns:
            QEmojiGrid, optional: The grid or None.
        """
        data = self.category(category)
        return data["grid"] if data else None

    def grids(self) -> typing.List[QEmojiGrid]:
        """Returns a list of all emoji grids.

        Returns:
            List[QEmojiGrid]: All grids.
        """
        return [data["grid"] for data in self.__categories_data.values()]

    def setFavoriteCategory(self, active: bool) -> None:
        """Enables or disables the favorites category.

        Args:
            active (bool): True to enable, False to disable.
        """
        favorite_category_key = self.EmojiCategory.Favorites.value
        favorite_category = self.category(favorite_category_key)
        if favorite_category is not None and not active:
            self.removeCategory(favorite_category_key)
        elif favorite_category is None and active:
            self.insertCategory(favorite_category_key, 0, favorite_category_key, self._icons[favorite_category_key])
            proxy = self.proxy(favorite_category_key)
            proxy.setFavoriteFilter(True)
            proxy.setCategoryFilter(None)
        self.__favorite_category = active

    def setRecentCategory(self, active: bool) -> None:
        """Enables or disables the recents category.

        Args:
            active (bool): True to enable, False to disable.
        """
        recent_category_key = self.EmojiCategory.Recents.value
        recent_category = self.category(recent_category_key)
        if recent_category is not None and not active:
            self.removeCategory(recent_category_key)
        elif recent_category is None and active:
            self.insertCategory(recent_category_key, 0, recent_category_key, self._icons[recent_category_key])
            proxy = self.proxy(recent_category_key)
            proxy.setRecentFilter(True)
            proxy.setCategoryFilter(None)
        self.__recent_category = active

    def _get_emoji_grid_font(self) -> QFont:
        """Returns the font to be used in the emoji grids.

        Returns:
            QFont: The calculated font.
        """
        font = QFont(self.emojiFont())
        size = self._get_emoji_icon_size()
        pixel_size = get_max_pixel_size("👏", font.family(), QSizeF(size, size))
        font.setPixelSize(pixel_size)
        return font

    def setEmojiFont(self, font_family: str) -> None:
        """Sets the font family for the emojis.

        Args:
            font_family (str): Font family name.
        """
        self.__emoji_font = font_family

        for grid in self.grids():
            grid.setFont(self._get_emoji_grid_font())

        for index, emoji in enumerate(self._skin_tone_selector_emojis.values()):
            skin_tone_selector_font = QFont(font_family)
            skin_tone_selector_font.setPixelSize(14)
            self.__skin_tone_selector.setItemFont(index, skin_tone_selector_font)

        emoji_label_font = QFont(font_family)
        emoji_label_font.setPixelSize(24)
        self.__emoji_label.setFont(emoji_label_font)

    def emojiFont(self) -> str:
        """Returns the current emoji font family.

        Returns:
            str: Font family name.
        """
        return self.__emoji_font

    def setEmojiSize(self, size: int) -> None:
        """Sets the size for the emoji items.

        Args:
            size (int): The new size.
        """
        if size != self.__emoji_size:
            self.__emoji_size = size
            qsize = QSize(size, size)

            for grid in self.grids():
                grid.setGridSize(qsize)
                grid.setIconSize(qsize)
                grid.setFont(self._get_emoji_grid_font())

            self.updateEmojiPixmapGetter()

    def emojiSize(self) -> int:
        """Returns the current emoji item size.

        Returns:
            int: The emoji size.
        """
        return self.__emoji_size

    def setEmojiPixmapGetter(self, emoji_pixmap_getter: typing.Optional[typing.Callable[[str, int, int, float], QPixmap]]) -> None:
        """Sets the function used to retrieve emoji pixmaps.

        This allows for custom emoji rendering (e.g., using Twemoji images).

        Args:
            emoji_pixmap_getter (Callable, optional): Pixmap getter function.
        """
        if emoji_pixmap_getter != self._emoji_pixmap_getter:
            self._emoji_pixmap_getter = emoji_pixmap_getter
            self.updateEmojiPixmapGetter()

            self._redraw_alias_emoji()
            self._redraw_skintones()

    def updateEmojiPixmapGetter(self) -> None:
        """Updates the pixmap getter for all proxy models."""
        emoji_pixmap_getter = self.emojiPixmapGetter()
        if emoji_pixmap_getter:
            margin = self.emojiSize() * 0.2
            size = self._get_emoji_icon_size()
            dpr = self.devicePixelRatio()

            for proxy in self.proxys():
                # Fix: Use a factory or default argument to capture the current state
                # to avoid issues with lambda late binding or references
                def make_getter(getter, m, s, d):
                    return lambda emoji: getter(emoji, m, s, d)

                proxy.setEmojiPixmapGetter(make_getter(emoji_pixmap_getter, margin, size, dpr))
        else:
            for proxy in self.proxys():
                proxy.setEmojiPixmapGetter(None)

    def emojiPixmapGetter(self) -> typing.Optional[typing.Callable[[str, int, int, float], QPixmap]]:
        """Returns the current emoji pixmap getter function."""
        return self._emoji_pixmap_getter