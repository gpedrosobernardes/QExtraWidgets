import typing

from PySide6.QtCore import QCoreApplication, Signal, QSize
from PySide6.QtGui import QAction, QStandardItem, QFont
from PySide6.QtWidgets import (QLineEdit, QHBoxLayout, QLabel, QVBoxLayout,
                               QMenu, QWidget, QApplication, QButtonGroup)
# Mocks for external libs mentioned in your original code
# from extra_qwidgets.widgets.accordion import QAccordion
from emojis.db import Emoji, get_emojis_by_category, get_categories
from typing import List

from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.widgets.accordion import QAccordion
from qextrawidgets.widgets.accordion_item import QAccordionItem
from qextrawidgets.widgets.emoji_picker.emoji_category import EmojiCategory
from qextrawidgets.widgets.emoji_picker.emoji_grid import QEmojiGrid
from qextrawidgets.emoji_utils import EmojiImageProvider
from qextrawidgets.widgets.search_line_edit import QSearchLineEdit


class QEmojiPicker(QWidget):
    # Signals
    picked = Signal(Emoji)  # Emoji object
    favorite = Signal(Emoji, QStandardItem)
    removedFavorite = Signal(Emoji, QStandardItem)  # renamed to camelCase

    _translations = {
        "Activities": QCoreApplication.translate("QEmojiPicker", "Activities"),
        "Food & Drink": QCoreApplication.translate("QEmojiPicker", "Food & Drink"),
        "Animals & Nature": QCoreApplication.translate("QEmojiPicker", "Animals & Nature"),
        "People & Body": QCoreApplication.translate("QEmojiPicker", "People & Body"),
        "Symbols": QCoreApplication.translate("QEmojiPicker", "Symbols"),
        "Flags": QCoreApplication.translate("QEmojiPicker", "Flags"),
        "Travel & Places": QCoreApplication.translate("QEmojiPicker", "Travel & Places"),
        "Objects": QCoreApplication.translate("QEmojiPicker", "Objects"),
        "Smileys & Emotion": QCoreApplication.translate("QEmojiPicker", "Smileys & Emotion"),
        "Favorites": QCoreApplication.translate("QEmojiPicker", "Favorites"),
        "Recent": QCoreApplication.translate("QEmojiPicker", "Recent")
    }

    def __init__(self, favorite_category: bool = True, recent_category: bool = True):
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
        self.__categories_data = {}  # Stores references to grids and layouts
        # Layout inside the scroll area where grids are located
        self.__accordion = QAccordion()

        # Main layout
        self.__main_layout = QVBoxLayout(self)
        self.__main_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Search Bar
        self.__line_edit = self._create_search_line_edit()

        self.__main_layout.addWidget(self.__line_edit)

        self._shortcuts_container = QWidget()
        self._shortcuts_container.setFixedHeight(40)  # Fixed height for the bar
        self._shortcuts_layout = QHBoxLayout(self._shortcuts_container)
        self._shortcuts_layout.setContentsMargins(5, 0, 5, 0)
        self._shortcuts_layout.setSpacing(2)

        self._shortcuts_group = QButtonGroup(self)
        self._shortcuts_group.setExclusive(True)
        self.__main_layout.addWidget(self._shortcuts_container)

        self.__emoji_label = QLabel()
        self.__emoji_label.setFixedSize(QSize(32, 32))
        self.__emoji_label.setScaledContents(True)
        self.__aliases_emoji_label = self._create_emoji_label()
        self._accordion = QAccordion()
        self.__menu_horizontal_layout = QHBoxLayout()
        self.__content_layout = QHBoxLayout()
        self.__content_layout.addWidget(self.__emoji_label)
        self.__content_layout.addWidget(self.__aliases_emoji_label, True)

        self.__main_layout.addWidget(self.__accordion)
        self.__main_layout.addLayout(self.__content_layout)

        self.__setup_connections()

        # Populates categories (Ideally this would be Lazy, called only when needed)
        self.__add_base_categories()

        self.setFavoriteCategory(favorite_category)
        self.setRecentCategory(recent_category)

        self.__accordion.expandAll()

    def __setup_connections(self):
        self.__line_edit.textChanged.connect(self.__filter_emojis)
        self.__accordion.enteredSection.connect(self.__on_entered_section)
        self.__accordion.leftSection.connect(self.__on_left_section)

    def __on_entered_section(self, section: QAccordionItem):
        category: EmojiCategory = self.__categories_data[section.objectName()]
        if section.header().isExpanded():
            category.shortcut().setChecked(True)

    def __on_left_section(self, section: QAccordionItem):
        category: EmojiCategory = self.__categories_data[section.objectName()]
        category.shortcut().setChecked(False)

    def __add_base_categories(self):
        """
        Creates categories.
        Note: In production, load items inside grids asynchronously or lazily.
        """
        # Example of static categories (replace with your DB call)
        for category_name in sorted(get_categories()):
            category = EmojiCategory(category_name, self._translations[category_name], self._icons[category_name])
            self.addCategory(category)
            self.__populate_grid_items(category.grid(), category_name)

    def _on_schortcut_clicked(self, section: QAccordionItem):
        self.__accordion.collapseAll()
        section.setExpanded(True)
        QApplication.processEvents()
        self.__accordion.scrollToItem(section)

    @staticmethod
    def __populate_grid_items(grid: QEmojiGrid, category: str):
        """Creates grid items."""
        # Here you would call get_emojis_by_category(category)
        # Mock Example:
        emojis_mock = get_emojis_by_category(category)

        for emoji in emojis_mock:
            grid.addEmoji(emoji, update_geometry=False)
        grid.updateGeometry()

    def __filter_emojis(self, text: str):
        """Filters all grids."""
        for category in self.__categories_data.values():
            grid = category.grid()
            section = category.accordionItem()

            grid.filterContent(text) # Calls grid filter method

            # If grid becomes empty after filter, hides title too
            is_empty = grid.allFiltered()
            grid.setVisible(not is_empty)
            section.setVisible(not is_empty)

    def __open_context_menu(self, emoji, item, global_pos):
        menu = QMenu(self)

        # Favorite Logic
        if self.__favorite_category:
            favorite_category = self.category("Favorites")
            grid = favorite_category.grid()
            if grid.emojiItem(emoji):
                action_unfav = QAction(self.tr("Remove from favorites"), self)
                action_unfav.triggered.connect(lambda: self.removedFavorite.emit(emoji, item))
                menu.addAction(action_unfav)
            else:
                action_fav = QAction(self.tr("Add to favorites"), self)
                action_fav.triggered.connect(lambda: self.favorite.emit(emoji, item))
                menu.addAction(action_fav)
        copy_alias = QAction(self.tr("Copy alias"), self)
        copy_alias.triggered.connect(lambda: self.__copy_emoji_alias(emoji))
        menu.addAction(copy_alias)

        menu.exec(global_pos)

    @staticmethod
    def __copy_emoji_alias(emoji: Emoji):
        clipboard = QApplication.clipboard()
        alias = emoji[0][0]
        clipboard.setText(f":{alias}:")

    def __on_mouse_enter_emoji(self, emoji: Emoji, item):
        pixmap = EmojiImageProvider.getPixmap(
            emoji,
            self.__emoji_label.size(),
            self.devicePixelRatio()
        )
        self.__emoji_label.setPixmap(pixmap)
        aliases = " ".join(f":{alias}:" for alias in emoji[0])
        self.__aliases_emoji_label.setText(aliases)

    def __on_mouse_left_emoji(self, emoji, item):
        self.__emoji_label.clear()
        self.__aliases_emoji_label.setText("")

    def __on_favorite(self, emoji: Emoji, _: QStandardItem):
        favorite_category = self.category("Favorites")
        grid = favorite_category.grid()
        grid.addEmoji(emoji)

    def __on_unfavorite(self, emoji: Emoji, _: QStandardItem):
        favorite_category = self.category("Favorites")
        grid = favorite_category.grid()
        grid.removeEmoji(emoji)

    def __add_recent(self, emoji: Emoji):
        recent_category = self.category("Recent")
        grid = recent_category.grid()
        if not grid.emojiItem(emoji):
            grid.addEmoji(emoji)

    @staticmethod
    def _create_emoji_label() -> QLabel:
        font = QFont()
        font.setBold(True)
        font.setPointSize(13)
        label = QLabel()
        label.setFont(font)
        return label

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

    # --- Public API (camelCase) ---

    def resetPicker(self):
        """Resets picker state."""
        self.__line_edit.clear()
        # Scroll to top
        self._accordion.scroll.verticalScrollBar().setValue(0)

    def addCategory(self, category: EmojiCategory, shortcut_position: int = -1, section_position: int = -1):
        self.__categories_data[category.name()] = category

        # Grid
        grid = category.grid()
        # Connect grid signals to Picker signals
        grid.emojiClicked.connect(lambda emoji, item: self.picked.emit(emoji))
        grid.mouseEnteredEmoji.connect(self.__on_mouse_enter_emoji)
        grid.mouseLeftEmoji.connect(self.__on_mouse_left_emoji)
        grid.contextMenu.connect(self.__open_context_menu)

        # Category Section
        section = category.accordionItem()
        self.__accordion.addAccordionItem(section, section_position)

        shortcut = category.shortcut()
        self._shortcuts_layout.insertWidget(shortcut_position, shortcut)
        self._shortcuts_group.addButton(shortcut)

        shortcut.clicked.connect(lambda: self._on_schortcut_clicked(section))

    def removeCategory(self, category: EmojiCategory):
        self.__categories_data.pop(category.name(), None)
        self.__accordion.removeAccordionItem(category.accordionItem())
        self._shortcuts_layout.removeWidget(category.shortcut())
        self._shortcuts_group.removeButton(category.shortcut())
        category.deleteLater()

    def categories(self) -> List[EmojiCategory]:
        return list(self.__categories_data.values())

    def category(self, name: str) -> typing.Optional[EmojiCategory]:
        return self.__categories_data.get(name)

    def setFavoriteCategory(self, active: bool):
        favorite_category = self.category("Favorites")
        if favorite_category and not active:
            self.removeCategory(favorite_category)
            self.favorite.disconnect(self.__on_favorite)
            self.removedFavorite.disconnect(self.__on_unfavorite)
        elif not favorite_category and active:
            category = EmojiCategory("Favorites", self._translations["Favorites"], self._icons["Favorites"])
            self.addCategory(category, 0, 0)
            self.favorite.connect(self.__on_favorite)
            self.removedFavorite.connect(self.__on_unfavorite)
        self.__favorite_category = active

    def setRecentCategory(self, active: bool):
        recent_category = self.category("Recent")
        if recent_category and not active:
            self.removeCategory(recent_category)
            self.picked.disconnect(self.__add_recent)
        elif not recent_category and active:
            category = EmojiCategory("Recent", self._translations["Recent"], self._icons["Recent"])
            self.addCategory(category, 0, 0)
            grid = category.grid()
            grid.setLimit(50)
            grid.setLimitTreatment(QEmojiGrid.LimitTreatment.RemoveFirstOne)
            self.picked.connect(self.__add_recent)
        self.__recent_category = active

    def accordion(self) -> QAccordion:
        return self.__accordion