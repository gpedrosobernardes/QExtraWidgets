import typing
from enum import Enum

from PySide6.QtCore import QCoreApplication, QSize, QT_TR_NOOP, QModelIndex, Signal, QPoint, Qt
from PySide6.QtGui import QFont, QIcon, QStandardItem, QFontMetrics, QPixmap
from PySide6.QtWidgets import (QLineEdit, QHBoxLayout, QLabel, QVBoxLayout,
                               QWidget, QApplication, QButtonGroup, QMenu, QToolButton)
from emoji_data_python import emoji_data

from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.utils import QEmojiFonts, get_max_pixel_size
from qextrawidgets.widgets.accordion import QAccordion
from qextrawidgets.widgets.accordion_item import QAccordionItem
from qextrawidgets.widgets.emoji_picker import QLazyLoadingEmojiDelegate
from qextrawidgets.widgets.emoji_picker.emoji_grid import QEmojiGrid
from qextrawidgets.widgets.emoji_picker.emoji_model import QEmojiModel
from qextrawidgets.widgets.emoji_picker.emoji_sort_filter import QEmojiSortFilterProxyModel
from qextrawidgets.widgets.emoji_picker.enums import QEmojiDataRole, EmojiSkinTone
from qextrawidgets.widgets.icon_combo_box import QIconComboBox
from qextrawidgets.widgets.search_line_edit import QSearchLineEdit


class QEmojiPicker(QWidget):
    picked = Signal(str)

    class EmojiCategories(Enum):
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
        Recent = QT_TR_NOOP("Recent")


    def __init__(self, favorite_category: bool = True, recent_category: bool = True, emoji_size = QSize(40, 40), emoji_font = None):
        super().__init__()

        self._icons = {
            self.EmojiCategories.Activities.value: QThemeResponsiveIcon.fromAwesome("fa6s.gamepad", options=[{"scale_factor": 0.9}]),
            self.EmojiCategories.FoodAndDrink.value: QThemeResponsiveIcon.fromAwesome("fa6s.bowl-food"),
            self.EmojiCategories.AnimalsAndNature.value: QThemeResponsiveIcon.fromAwesome("fa6s.leaf"),
            self.EmojiCategories.PeopleAndBody.value: QThemeResponsiveIcon.fromAwesome("fa6s.user"),
            self.EmojiCategories.Symbols.value: QThemeResponsiveIcon.fromAwesome("fa6s.heart"),
            self.EmojiCategories.Flags.value: QThemeResponsiveIcon.fromAwesome("fa6s.flag"),
            self.EmojiCategories.TravelAndPlaces.value: QThemeResponsiveIcon.fromAwesome("fa6s.bicycle", options=[{"scale_factor": 0.9}]),
            self.EmojiCategories.Objects.value: QThemeResponsiveIcon.fromAwesome("fa6s.lightbulb"),
            self.EmojiCategories.SmileysAndEmotion.value: QThemeResponsiveIcon.fromAwesome("fa6s.face-smile"),
            self.EmojiCategories.Favorites.value: QThemeResponsiveIcon.fromAwesome("fa6s.star"),
            self.EmojiCategories.Recent.value: QThemeResponsiveIcon.fromAwesome("fa6s.clock-rotate-left")
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
        self.__favorite_category_index = None
        self.__recent_category_index = None
        self._emoji_pixmap_getter = None
        self._emoji_on_label = None
        self.__categories_data = []  # Stores references to grids and layouts
        # Layout inside the scroll area where grids are located

        self.__emoji_size = None
        if emoji_font is None:
            emoji_font = QEmojiFonts.twemojiFont()
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
        self._accordion = QAccordion()
        self.__menu_horizontal_layout = QHBoxLayout()

        self.__setup_connections()

        # Populates categories (Ideally this would be Lazy, called only when needed)
        self.__add_base_categories()

        self.setFavoriteCategory(favorite_category)
        self.setRecentCategory(recent_category)

        self.__accordion.expandAll()

        self.setEmojiFont(emoji_font)
        self.setEmojiSize(emoji_size)

        self.__setup_layout()

    def __setup_layout(self):
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

    def _set_skin_tone(self, skin_tone: str):
        self.__model.setSkinTone(skin_tone)
        self._redraw_emoji_items(self.__model.filterEmojisItems(QEmojiDataRole.HasSkinTonesRole, True))

    def __setup_connections(self):
        self.__search_line_edit.textChanged.connect(self.__filter_emojis)
        self.__accordion.enteredSection.connect(self.__on_entered_section)
        self.__skin_tone_selector.currentDataChanged.connect(self._set_skin_tone)

    def __on_entered_section(self, section: QAccordionItem):
        shortcut = self.shortcut(self.sections().index(section))
        if section.header().isExpanded():
            shortcut.setChecked(True)

    def __filter_emojis(self):
        text = self.__search_line_edit.text()

        for proxy, section in zip(self.proxys(), self.sections()):
            proxy.setFilterFixedString(text)
            section.setVisible(proxy.rowCount() != 0 or not text)

    def __on_hover_emoji(self, index: QModelIndex):
        item = self.__model.itemFromProxyIndex(index)
        alias = item.data(QEmojiDataRole.AliasRole)
        metrics = QFontMetrics(self.__aliases_emoji_label.font())
        elided_alias = metrics.elidedText(alias, Qt.TextElideMode.ElideRight, self.__aliases_emoji_label.width())
        self.__aliases_emoji_label.setText(elided_alias)
        self._emoji_on_label = item.data(Qt.ItemDataRole.UserRole)
        self._redraw_alias_emoji()

    def __clear_emoji_preview(self):
        self._emoji_on_label = None
        self.__emoji_label.clear()
        self.__current_alias = ""
        self.__aliases_emoji_label.clear()

    def __on_emoji_clicked(self, proxy_index: QModelIndex):
        item = self.__model.itemFromProxyIndex(proxy_index)
        item.setData(True, QEmojiDataRole.RecentRole)
        self.picked.emit(item.text())

    def __item_from_position(self, list_view: QEmojiGrid, position: QPoint) -> typing.Optional[QStandardItem]:
        proxy_index = list_view.indexAt(position)
        if not proxy_index:
            return None
        return self.__model.itemFromProxyIndex(proxy_index)

    def __on_context_menu(self, grid: QEmojiGrid, position: QPoint):
        menu = QMenu()
        item = self.__item_from_position(grid, position)

        if not item:
            return

        if self.__favorite_category:
            item_favorited = item.data(QEmojiDataRole.FavoriteRole)

            if item_favorited:
                action = menu.addAction("Unfavorite")
                action.triggered.connect(lambda: item.setData(False, QEmojiDataRole.FavoriteRole))
                menu.addAction(action)
            else:
                action = menu.addAction("Favorite")
                action.triggered.connect(lambda: item.setData(True, QEmojiDataRole.FavoriteRole))

        copy_alias_action = menu.addAction("Copy alias")
        copy_alias_action.triggered.connect(lambda: QApplication.clipboard().setText(item.data(QEmojiDataRole.AliasRole)))

        menu.exec(grid.mapToGlobal(position))

    def __add_base_categories(self):
        """
        Creates categories.
        Note: In production, load items inside grids asynchronously or lazily.
        """
        categories = []

        for data in sorted(emoji_data, key=lambda emoji_: emoji_.sort_order):
            if data.has_img_twitter and data.category != "Component":

                if data.category not in categories:
                    categories.append(data.category)
                    self.addCategory(data.category, self._icons[data.category])

                if data.skin_variations:
                    skin_tones = {skin_tone: found_skin_tone.char for skin_tone in list(EmojiSkinTone) if (found_skin_tone := data.skin_variations.get(skin_tone.value))}
                    if skin_tones:
                        skin_tones[EmojiSkinTone.Default.value] = data.char
                    else:
                        skin_tones = None
                else:
                    skin_tones = None

                self.__model.addEmoji(data.char, " ".join(f":{alias}:" for alias in data.short_names), data.category, skin_tones=skin_tones)

    def _on_shortcut_clicked(self, section: QAccordionItem):
        self.__accordion.collapseAll()
        section.setExpanded(True)
        QApplication.processEvents()
        self.__accordion.scrollToItem(section)

    def _set_emoji_icon(self, item: QStandardItem):
        if not item.icon():
            emoji_pixmap_getter = self.emojiPixmapGetter()
            emoji = item.data(Qt.ItemDataRole.UserRole)
            dpr = self.devicePixelRatio()
            item.setIcon(emoji_pixmap_getter(emoji, QSize(100, 100), dpr))

    def _redraw_emoji_items(self, items: typing.Optional[typing.List[QStandardItem]] = None):
        emoji_pixmap_getter = self.emojiPixmapGetter()

        if items is None:
            items = self.__model.getEmojiItems()

        for item in items:
            if emoji_pixmap_getter:
                if item.text():
                    item.setText("")
                if item.icon():
                    item.setIcon(QIcon())
            else:
                item.setText(item.data(Qt.ItemDataRole.UserRole))

    def _redraw_skintones(self):
        emoji_pixmap_getter = self.emojiPixmapGetter()

        for index, emoji in enumerate(self._skin_tone_selector_emojis.values()):
            if emoji_pixmap_getter:
                size = self.__skin_tone_selector.iconSize()
                dpr = self.devicePixelRatio()
                self.__skin_tone_selector.setItemIcon(index, emoji_pixmap_getter(emoji, size, dpr))
            else:
                self.__skin_tone_selector.setItemText(index, emoji)

    def _redraw_alias_emoji(self):
        if self._emoji_on_label:
            emoji_pixmap_getter = self.emojiPixmapGetter()

            if emoji_pixmap_getter:
                pixmap = emoji_pixmap_getter(self._emoji_on_label, self.emojiSize(), self.devicePixelRatio())
                self.__emoji_label.setPixmap(pixmap)
            else:
                self.__emoji_label.setText(self._emoji_on_label)

    @staticmethod
    def _create_search_line_edit() -> QLineEdit:
        font = QFont()
        font.setPointSize(12)
        line_edit = QSearchLineEdit()
        line_edit.setFont(font)
        line_edit.setPlaceholderText(
            QCoreApplication.translate("QEmojiPicker", "Search emoji...")
        )
        return line_edit

    @staticmethod
    def _create_emoji_label() -> QLabel:
        font = QFont()
        font.setBold(True)
        font.setPointSize(13)
        label = QLabel()
        label.setFont(font)
        return label

    @staticmethod
    def _create_shortcut_button(text: str, icon: QIcon) -> QToolButton:
        btn = QToolButton()
        btn.setCheckable(True)
        btn.setAutoRaise(True)  # Visual flat/clean
        btn.setFixedSize(32, 32)
        btn.setIconSize(QSize(22, 22))
        btn.setToolTip(text)
        btn.setText(text)
        btn.setIcon(icon)
        return btn

    @staticmethod
    def _create_grid() -> QEmojiGrid:
        return QEmojiGrid()

    # --- Public API (camelCase) ---

    def resetPicker(self):
        """Resets picker state."""
        self.__search_line_edit.clear()
        self._accordion.resetScroll()

    def addCategory(self, text: str, icon: QIcon) -> int:
        index = len(self.__categories_data)
        self.insertCategory(index, text, icon)
        return index

    def insertCategory(self, index: int, text: str, icon: QIcon):
        # Proxy
        proxy = QEmojiSortFilterProxyModel()
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
        grid.customContextMenuRequested.connect(lambda pos: self.__on_context_menu(grid, pos))

        category_data = dict(grid=grid, shortcut=shortcut, section=section, proxy=proxy)
        self.__categories_data.insert(index, category_data)
        return self.__categories_data.index(category_data)

    def removeCategory(self, index: int):
        section, shortcut, grid = self.section(index), self.shortcut(index), self.grid(index)

        self.__accordion.removeAccordionItem(section)
        self._shortcuts_layout.removeWidget(shortcut)
        self._shortcuts_group.removeButton(shortcut)

        section.deleteLater()
        grid.deleteLater()
        shortcut.deleteLater()

        self.__categories_data.pop(index)

    def accordion(self) -> QAccordion:
        return self.__accordion

    def model(self) -> QEmojiModel:
        return self.__model

    def proxy(self, index: int) -> QEmojiSortFilterProxyModel:
        return self.__categories_data[index]["proxy"]

    def proxys(self) -> typing.List[QEmojiSortFilterProxyModel]:
        return [data["proxy"] for data in self.__categories_data]

    def shortcut(self, index: int) -> QToolButton:
        return self.__categories_data[index]["shortcut"]

    def section(self, index: int) -> QAccordionItem:
        return self.__categories_data[index]["section"]

    def sections(self) -> typing.List[QAccordionItem]:
        return [data["section"] for data in self.__categories_data]

    def grid(self, index: int) -> QEmojiGrid:
        return self.__categories_data[index]["grid"]

    def grids(self) -> typing.List[QEmojiGrid]:
        return [data["grid"] for data in self.__categories_data]

    def setFavoriteCategory(self, active: bool):
        if self.__favorite_category_index is not None and not active:
            self.removeCategory(self.__favorite_category_index)
            self.__favorite_category_index = None
        elif self.__favorite_category_index is None and active:
            favorite_category = self.EmojiCategories.Favorites.value
            index = self.insertCategory(0, favorite_category, self._icons[favorite_category])
            proxy = self.proxy(index)
            proxy.setFavoriteFilter(True)
            proxy.setCategoryFilter(None)
            self.__favorite_category_index = index
        self.__favorite_category = active

    def setRecentCategory(self, active: bool):
        if self.__recent_category_index is not None and not active:
            self.removeCategory(self.__recent_category_index)
            self.__recent_category_index = None
        elif self.__recent_category_index is None and active:
            recent_category = self.EmojiCategories.Recent.value
            index = self.insertCategory(0, recent_category, self._icons[recent_category])
            proxy = self.proxy(index)
            proxy.setRecentFilter(True)
            proxy.setCategoryFilter(None)
            self.__recent_category_index = index
        self.__recent_category = active

    def setEmojiFont(self, font: QFont):
        self.__emoji_font = font

        for grid in self.grids():
            grid.setFont(font)

        emoji_label_font = QFont(font)
        emoji_label_font.setPixelSize(24)
        self.__emoji_label.setFont(emoji_label_font)

    def emojiFont(self) -> QFont:
        return self.__emoji_font

    def setEmojiSize(self, size: QSize):
        if size != self.__emoji_size:
            self.__emoji_size = size

            for grid in self.grids():
                grid.setGridSize(size)

                size_with_margin = size * 0.8
                grid.setIconSize(size_with_margin)

                font = QFont(self.emojiFont())
                pixel_size = get_max_pixel_size("👏", font.family(), size_with_margin)
                font.setPixelSize(pixel_size)
                grid.setFont(font)

            self.__model.setEmojiSize(size)

    def emojiSize(self) -> QSize:
        return self.__emoji_size

    def setEmojiPixmapGetter(self, emoji_pixmap_getter: typing.Optional[typing.Callable[[str, QSize, float], QPixmap]]):
        if emoji_pixmap_getter != self._emoji_pixmap_getter:
            self._emoji_pixmap_getter = emoji_pixmap_getter

            if emoji_pixmap_getter:
                for grid in self.grids():
                    delegate = QLazyLoadingEmojiDelegate()
                    delegate.painted.connect(lambda proxy_index: self._set_emoji_icon(self.__model.itemFromProxyIndex(proxy_index)))
                    grid.setItemDelegate(delegate)
            else:
                for grid in self.grids():
                    delegate = grid.itemDelegate()
                    if isinstance(delegate, QLazyLoadingEmojiDelegate):
                        delegate.painted.disconnect()
                        grid.setItemDelegate(None)

            self._redraw_emoji_items()
            self._redraw_alias_emoji()
            self._redraw_skintones()

    def emojiPixmapGetter(self) -> typing.Optional[typing.Callable[[str, QSize, float], QPixmap]]:
        return self._emoji_pixmap_getter