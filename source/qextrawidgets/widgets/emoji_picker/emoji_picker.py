import typing
from enum import Enum

from PySide6.QtCore import QCoreApplication, QSize, QT_TR_NOOP, QModelIndex, Signal, QPoint, Qt
from PySide6.QtGui import QFont, QIcon, QStandardItem
from PySide6.QtWidgets import (QLineEdit, QHBoxLayout, QLabel, QVBoxLayout,
                               QWidget, QApplication, QButtonGroup, QToolButton, QMenu)
from emoji_data_python import emoji_data

from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.utils import QEmojiFonts
from qextrawidgets.widgets.QExtraToolButton import QExtraToolButton
from qextrawidgets.widgets.icon_combo_box import QIconComboBox
from qextrawidgets.widgets.accordion import QAccordion
from qextrawidgets.widgets.accordion_item import QAccordionItem
from qextrawidgets.widgets.emoji_picker import QLazyLoadingEmojiDelegate
from qextrawidgets.widgets.emoji_picker.emoji_grid import QEmojiGrid
from qextrawidgets.widgets.emoji_picker.emoji_model import QEmojiModel, QEmojiDataRole
from qextrawidgets.widgets.emoji_picker.emoji_sort_filter import QEmojiSortFilterProxyModel
from qextrawidgets.widgets.search_line_edit import QSearchLineEdit


class QEmojiPicker(QWidget):
    picked = Signal(str)

    SkinTones = {'': '👏', '1F3FB': '👏🏻', '1F3FC': '👏🏼', '1F3FD': '👏🏽', '1F3FE': '👏🏾', '1F3FF': '👏🏿'}

    class EmojiCategories(Enum):
        Activies = QT_TR_NOOP("Activities")
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
            "Activities": QThemeResponsiveIcon.fromAwesome("fa6s.gamepad", options=[{"scale_factor": 0.9}]),
            "Food & Drink": QThemeResponsiveIcon.fromAwesome("fa6s.bowl-food"),
            "Animals & Nature": QThemeResponsiveIcon.fromAwesome("fa6s.leaf"),
            "People & Body": QThemeResponsiveIcon.fromAwesome("fa6s.user"),
            "Symbols": QThemeResponsiveIcon.fromAwesome("fa6s.heart"),
            "Flags": QThemeResponsiveIcon.fromAwesome("fa6s.flag"),
            "Travel & Places": QThemeResponsiveIcon.fromAwesome("fa6s.bicycle", options=[{"scale_factor": 0.9}]),
            "Objects": QThemeResponsiveIcon.fromAwesome("fa6s.lightbulb"),
            "Smileys & Emotion": QThemeResponsiveIcon.fromAwesome("fa6s.face-smile"),
            "Favorites": QThemeResponsiveIcon.fromAwesome("fa6s.star"),
            "Recent": QThemeResponsiveIcon.fromAwesome("fa6s.clock-rotate-left")
        }

        # Private variables
        self.__favorite_category = None
        self.__recent_category = None
        self.__favorite_category_index = None
        self.__recent_category_index = None
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


        for key, emoji in self.SkinTones.items():
            self.__skin_tone_selector.addItem(text=emoji, data=key, font=QFont(emoji_font))

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


    def __setup_connections(self):
        self.__search_line_edit.textChanged.connect(self.__filter_emojis)
        self.__accordion.enteredSection.connect(self.__on_entered_section)
        # self.__accordion.leftSection.connect(self.__on_left_section)
        self.__skin_tone_selector.currentDataChanged.connect(self.__change_skin_tone)

    def __change_skin_tone(self, key: str):
        for row in range(self.__model.rowCount()):
            item = self.__model.item(row)
            skin_tones: dict = item.data(QEmojiDataRole.SkinTonesRole)
            if skin_tones:
                if key in skin_tones:
                    item.setText(skin_tones[key].char)
                else:
                    item.setText(item.data(QEmojiDataRole.YellowEmojiRole))

    def __on_entered_section(self, section: QAccordionItem):
        sections = [category_data["section"] for category_data in self.__categories_data]
        category_data = self.__categories_data[sections.index(section)]
        if section.header().isExpanded():
            category_data["shortcut"].setChecked(True)

    def __filter_emojis(self):
        for category_data in self.__categories_data:
            text = self.__search_line_edit.text()
            proxy = category_data["proxy"]
            proxy.setFilterFixedString(text)
            section = category_data["section"]
            section.setVisible(proxy.rowCount() != 0 or not text)

    def __on_hover_emoji(self, item: QStandardItem):
        alias = item.data(QEmojiDataRole.AliasRole)
        self.__aliases_emoji_label.setText(alias)
        emoji = item.text()
        emoji_delegate = self.emojiDelegate()
        self.__emoji_label.clear()
        if emoji_delegate:
            emoji_image_getter = emoji_delegate.emojiImageGetter()
            pixmap = emoji_image_getter(emoji, self.emojiSize(), self.devicePixelRatio())
            self.__emoji_label.setPixmap(pixmap)
        else:
            self.__emoji_label.setText(emoji)

    def __on_emoji_clicked(self, item: QStandardItem):
        self.picked.emit(item.text())
        item.setData(True, QEmojiDataRole.RecentRole)

    def __item_from_proxy(self, proxy: QEmojiSortFilterProxyModel, proxy_index: QModelIndex):
        model_index = proxy.mapToSource(proxy_index)
        return self.__model.itemFromIndex(model_index)

    def __item_from_position(self, list_view: QEmojiGrid, position: QPoint):
        proxy_index = list_view.indexAt(position)
        return self.__item_from_proxy(list_view.model(), proxy_index)

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

                self.__model.addEmoji(data.char, " ".join(f":{alias}:" for alias in data.short_names), data.category, skin_tones=data.skin_variations)

    def _on_schortcut_clicked(self, section: QAccordionItem):
        self.__accordion.collapseAll()
        section.setExpanded(True)
        QApplication.processEvents()
        self.__accordion.scrollToItem(section)

    def _update_grid_font(self, grid: QEmojiGrid, size: int):
        font = self.emojiFont()
        font.setPixelSize(size)
        grid.setFont(font)

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
    def _create_shortcut_button(text: str, icon: QIcon) -> QExtraToolButton:
        btn = QExtraToolButton()
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
        # Scroll to top
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
        shortcut.clicked.connect(lambda: self._on_schortcut_clicked(section))
        grid.entered.connect(lambda _index: self.__on_hover_emoji(self.__item_from_proxy(proxy, _index)))
        grid.clicked.connect(lambda _index: self.__on_emoji_clicked(self.__item_from_proxy(proxy, _index)))
        grid.customContextMenuRequested.connect(lambda pos: self.__on_context_menu(grid, pos))

        category_data = dict(grid=grid, shortcut=shortcut, section=section, proxy=proxy)
        self.__categories_data.insert(index, category_data)
        return self.__categories_data.index(category_data)

    def removeCategory(self, index: int):
        items = self.__categories_data.pop(index)

        self.__accordion.removeAccordionItem(items["section"])
        self._shortcuts_layout.removeWidget(items["shortcut"])
        self._shortcuts_group.removeButton(items["shortcut"])
        items["grid"].deleteLater()
        items["shortcut"].deleteLater()
        items["section"].deleteLater()

    def accordion(self) -> QAccordion:
        return self.__accordion

    def model(self) -> QEmojiModel:
        return self.__model

    def proxy(self, index: int) -> QEmojiSortFilterProxyModel:
        return self.__categories_data[index]["proxy"]

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
                grid.setIconSize(size)
                self._update_grid_font(grid, self.emojiSize().height() * 0.5)

            # Usamos o tamanho cheio para o sizeHint do modelo.
            # Se usarmos size * 0.9 aqui, alguns estilos de sistema desenharão
            # a seleção/hover em um retângulo menor que o grid cell, causando inconsistência.
            # O delegate se encarrega de aplicar a margem apenas no desenho do emoji.
            self.__model.setEmojiSize(size)

    def emojiSize(self) -> QSize:
        return self.__emoji_size

    def setEmojiDelegate(self, emoji_delegate: QLazyLoadingEmojiDelegate):
        self.__emoji_delegate = emoji_delegate

        for grid in self.grids():
            grid.setItemDelegate(emoji_delegate)

        for index, emoji in enumerate(self.SkinTones.values()):
            size = self.__skin_tone_selector.iconSize()
            dpr = self.devicePixelRatio()
            getter = emoji_delegate.emojiImageGetter()
            self.__skin_tone_selector.setItemIcon(index, getter(emoji, size, dpr))

    def emojiDelegate(self) -> typing.Optional[QLazyLoadingEmojiDelegate]:
        return self.__emoji_delegate