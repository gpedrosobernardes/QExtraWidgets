import contextlib
import typing
from abc import abstractmethod

import qtawesome
from PySide6.QtCore import QCoreApplication, Signal, QSize, QTimer, QPoint, Qt
from PySide6.QtGui import QIcon, QPixmap, QAction, QStandardItem
from PySide6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QLabel, QVBoxLayout, \
    QScrollArea, QMenu, QAbstractButton
from emojis.db import Emoji, get_emojis_by_category

from extra_qwidgets.abc_widgets.abc_collapse_group import ABCCollapseGroup
from extra_qwidgets.exceptions import FavoriteNotImplemented, RecentNotImplemented, EmojiAlreadyExists
from extra_qwidgets.utils import get_emoji_path
from extra_qwidgets.widgets.emoji_picker.emoji_grid import QEmojiGrid

translate = QCoreApplication.translate


class ABCEmojiPicker(QWidget):
    picked = Signal(Emoji)
    favorite = Signal(Emoji)
    removed_favorite = Signal(Emoji)

    def __init__(self, favorite_category: bool = True, recent_category: bool = True):
        super().__init__()
        self.__favorite_category = favorite_category
        self.__recent_category = recent_category
        self.__line_edit = self._new_search_line_edit()
        self.__line_edit.setPlaceholderText(
            translate("QEmojiPicker", "Enter your favorite emoji")
        )
        self.__categories = {}
        self.__emoji_label = QLabel()
        self.__emoji_label.setFixedSize(QSize(32, 32))
        self.__emoji_label.setScaledContents(True)
        self.__aliases_emoji_label = self._new_emoji_label()
        self._collapse_group = self._new_collapse_group()
        self.__menu_horizontal_layout = QHBoxLayout()
        self.__scroll_area = QScrollArea()
        self.__scroll_area.setWidgetResizable(True)
        #self.__scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.__scroll_area.setWidget(self._collapse_group)
        self.__emoji_layout = QHBoxLayout()
        self.__emoji_layout.addWidget(self.__emoji_label)
        self.__emoji_layout.addWidget(self.__aliases_emoji_label, True)
        self.__vertical_layout = QVBoxLayout()
        self.__vertical_layout.addLayout(self.__menu_horizontal_layout)
        self.__vertical_layout.addWidget(self.__line_edit)
        self.__vertical_layout.addWidget(self.__scroll_area)
        self.__vertical_layout.addLayout(self.__emoji_layout)
        self.setLayout(self.__vertical_layout)
        self.__add_categories()
        self.__load_emojis()
        # self.__hide_empty_categories()
        # self.__bind_signals()

    def __bind_signals(self):
        self.__line_edit.textEdited.connect(lambda: self.__filter_emojis(self.__line_edit.text()))
        self.__line_edit.textEdited.connect(lambda: QTimer.singleShot(5, self.__hide_empty_categories))

        if self.__favorite_category:
            self.favorite.connect(lambda emoji: self.addFavorite(emoji))
            self.favorite.connect(lambda: self.__filter_emojis(self.__line_edit.text()))
            self.favorite.connect(lambda: QTimer.singleShot(5, self.__hide_empty_categories))
            self.removed_favorite.connect(lambda emoji: self.removeFavorite(emoji))
            self.removed_favorite.connect(lambda: self.__filter_emojis(self.__line_edit.text()))
            self.removed_favorite.connect(lambda: QTimer.singleShot(5, self.__hide_empty_categories))

    def __add_categories(self):
        if self.__recent_category:
            self.add_category(
                "Recent",
                qtawesome.icon("fa6s.clock-rotate-left"),
                translate("QEmojiPicker", "Recent"),
            )
        if self.__favorite_category:
            self.add_category(
                "Favorite",
                qtawesome.icon("fa6s.star"),
                translate("QEmojiPicker", "Favorite"),
            )
        self.add_category(
            "Smileys & Emotion",
            qtawesome.icon("fa6s.face-smile"),
            translate("QEmojiPicker", "Smileys & Emotion"),
        )
        self.add_category(
            "Animals & Nature",
            qtawesome.icon("fa6s.leaf"),
            translate("QEmojiPicker", "Animals & Nature"),
        )
        self.add_category(
            "Food & Drink",
            qtawesome.icon("fa6s.bowl-food"),
            translate("QEmojiPicker", "Food & Drink"),
        )
        self.add_category(
            "Activities",
            qtawesome.icon("fa6s.gamepad"),
            translate("QEmojiPicker", "Activities"),
        )
        self.add_category(
            "Travel & Places",
            qtawesome.icon("fa6s.bicycle"),
            translate("QEmojiPicker", "Travel & Places"),
        )
        self.add_category(
            "Objects",
            qtawesome.icon("fa6s.lightbulb"),
            translate("QEmojiPicker", "Objects"),
        )
        self.add_category(
            "Symbols",
            qtawesome.icon("fa6s.heart"),
            translate("QEmojiPicker", "Symbols"),
        )
        self.add_category(
            "Flags",
            qtawesome.icon("fa6s.flag"),
            translate("QEmojiPicker", "Flags"),
        )

    def __load_emojis(self):
        for category in self.__categories.keys():
            if category not in ("Favorite", "Recent"):
                self.__add_emojis(category, get_emojis_by_category(category))
                self.emojiGrid(category)._adjust_fixed_height()
        self.__add_emojis("Smileys & Emotion", get_emojis_by_category("People & Body"))

    def add_category(self, category: str, icon: QIcon, title: str):
        shortcut_button = self._new_shortcut_button()
        shortcut_button.setIcon(icon)
        shortcut_button.clicked.connect(lambda: self.__on_shortcut_click(category))
        self.__menu_horizontal_layout.addWidget(shortcut_button)
        emoji_grid = QEmojiGrid()
        self._collapse_group.addCollapse(title, emoji_grid, name=category, stretch=True)
        self.__categories[category] = {
            "shortcut": shortcut_button,
            "grid": emoji_grid
        }

    def __collapse_all_but(self, category: str):
        self._collapse_group.collapseAll()
        self._collapse_group.setCollapsedByName(False, category)

    def __scroll_to_category(self, category: str):
        self.__scroll_area.verticalScrollBar().setValue(
            self.emojiGrid(category).y()
        )

    def __on_shortcut_click(self, category: str):
        self.__collapse_all_but(category)
        QTimer.singleShot(5, lambda: self.__scroll_to_category(category))

    def emojiGrid(self, category: str) -> QEmojiGrid:
        return self.__categories[category]["grid"]

    def shortcut(self, category: str) -> QAbstractButton:
        return self.__categories[category]["shortcut"]

    def __add_emojis(self, category: str, emojis_: typing.List[Emoji]):
        for emoji in emojis_:
            self.__add_emoji(category, emoji)

    def __add_emoji(self, category: str, emoji: Emoji) -> QStandardItem:
        emoji_grid = self.emojiGrid(category)
        item = QStandardItem()
        item.setData(emoji, Qt.ItemDataRole.UserRole)
        item.setIcon(QIcon(get_emoji_path(emoji)))
        self.__bind_emoji_item(item, emoji)
        emoji_grid.addItem(item)
        return item

    @abstractmethod
    def _new_emoji_label(self) -> QLabel:
        pass

    @abstractmethod
    def _new_search_line_edit(self) -> QLineEdit:
        pass

    @abstractmethod
    def _new_shortcut_button(self) -> QAbstractButton:
        pass

    @abstractmethod
    def _new_collapse_group(self) -> ABCCollapseGroup:
        pass

    def __remove_emoji(self, category: str, emoji: Emoji):
        emoji_grid = self.emojiGrid(category)
        emoji_grid.removeEmoji(emoji)

    def __bind_emoji_item(self, emoji_item: QStandardItem, emoji: Emoji):
        emoji_item.enterEvent = lambda event: self.__set_emoji_label(emoji)
        emoji_item.leaveEvent = lambda event: self.__mouse_leave_emoji()
        # if self.__favorite_category:
        #     emoji_item.setContextMenuPolicy(
        #         Qt.ContextMenuPolicy.CustomContextMenu
        #     )
        #     emoji_item.customContextMenuRequested.connect(
        #         lambda position: self.__open_button_context_menu(position, emoji_item)
        #     )
        # emoji_item.clicked.connect(lambda: self.picked.emit(emoji))
        # if self.__recent_category:
        #     emoji_item.clicked.connect(lambda: self.__add_recent(emoji))
        #     emoji_item.clicked.connect(lambda: self.__filter_emojis(self.__line_edit.text()))
        #     emoji_item.clicked.connect(lambda: QTimer.singleShot(5, self.__hide_empty_categories))

    def addRecent(self, emoji: Emoji):
        if not self.__recent_category:
            raise RecentNotImplemented()

        if self.isRecent(emoji):
            raise EmojiAlreadyExists(emoji.emoji)

        self.__add_emoji("Recent", emoji)
        self.emojiGrid("Recent").filter(self.__line_edit.text())

    def __add_recent(self, emoji: Emoji):
        with contextlib.suppress(EmojiAlreadyExists):
            self.addRecent(emoji)

    def isRecent(self, emoji: Emoji) -> bool:
        if not self.__recent_category:
            raise RecentNotImplemented()

        emoji_grid = self.emojiGrid("Recent")
        return bool(emoji_grid.getItem(emoji))

    def removeRecent(self, emoji: Emoji):
        if not self.__recent_category:
            raise RecentNotImplemented()

        self.__remove_emoji("Recent", emoji)

    def addFavorite(self, emoji: Emoji):
        if not self.__favorite_category:
            raise FavoriteNotImplemented()

        if self.isFavorite(emoji):
            raise EmojiAlreadyExists(emoji.emoji)

        self.__add_emoji("Favorite", emoji)

    def isFavorite(self, emoji: Emoji) -> bool:
        if not self.__favorite_category:
            raise FavoriteNotImplemented()

        emoji_grid = self.emojiGrid("Favorite")
        return bool(emoji_grid.getItem(emoji))

    def removeFavorite(self, emoji: Emoji):
        if not self.__favorite_category:
            raise FavoriteNotImplemented()

        self.__remove_emoji("Favorite", emoji)

    def emojiItem(self, emoji: Emoji) -> typing.Optional[QStandardItem]:
        for category in self.__categories.keys():
            if category not in ("Favorite", "Recent"):
                emoji_grid = self.emojiGrid(category)
                emoji_item = emoji_grid.getItem(emoji)
                return emoji_item
        return None

    def __set_emoji_label(self, emoji: Emoji):
        aliases = " ".join(map(lambda alias: f":{alias}:", emoji.aliases))
        self.__emoji_label.setPixmap(QPixmap(get_emoji_path(emoji)))
        self.__aliases_emoji_label.setText(aliases)

    def __hide_empty_categories(self):
        for category in self.__categories.keys():
            emoji_grid = self.emojiGrid(category)
            is_empty = emoji_grid.isEmpty()
            self._collapse_group.setCollapsedByName(is_empty, category)
            shortcut = self.shortcut(category)
            shortcut.setHidden(is_empty)

    def __filter_emojis(self, emoji_alias: str = ""):
        for category in self.__categories.keys():
            emoji_grid = self.emojiGrid(category)
            emoji_grid.filter(emoji_alias)

    def __mouse_leave_emoji(self):
        self.__emoji_label.clear()
        self.__aliases_emoji_label.clear()

    def reset(self):
        self.__line_edit.clear()
        self.__filter_emojis()
        self.__scroll_area.verticalScrollBar().setValue(0)

    def __open_button_context_menu(self, position: QPoint, button: QAbstractButton):
        context_menu = QMenu()
        emoji = button.property("emoji")
        if self.isFavorite(emoji):
            remove_action = QAction(
                translate("QEmojiPicker", "Remove from favorite")
            )
            remove_action.triggered.connect(lambda: self.removed_favorite.emit(emoji))
            context_menu.addAction(remove_action)
        else:
            add_action = QAction(translate("QEmojiPicker", "Add to favorite"))
            add_action.triggered.connect(lambda: self.favorite.emit(emoji))
            context_menu.addAction(add_action)
        context_menu.exec(button.mapToGlobal(position))