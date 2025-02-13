import contextlib
import typing
from PySide6.QtCore import QCoreApplication, Signal, QSize, QTimer, QPoint, Qt
from PySide6.QtGui import QIcon, QFont, QPixmap, QAction
from PySide6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QLabel, QVBoxLayout, \
    QScrollArea, QMenu
from emojis.db import Emoji, get_emojis_by_category

from extra_qwidgets.widgets.collapse_group import QCollapseGroup
from extra_qwidgets.widgets.theme_responsive_button import QThemeResponsiveButton
from extra_qwidgets.widgets.emoji_picker.emoji_button import QEmojiButton
from extra_qwidgets.widgets.emoji_picker.emoji_grid import QEmojiGrid
from extra_qwidgets.exceptions import FavoriteNotImplemented, RecentNotImplemented, EmojiAlreadyExists
from extra_qwidgets.utils import get_awesome_icon, get_emoji_path

translate = QCoreApplication.translate


class QEmojiPicker(QWidget):
    picked = Signal(Emoji)
    favorite = Signal(Emoji)
    removed_favorite = Signal(Emoji)
    __aliases_emoji_font = QFont()
    __aliases_emoji_font.setBold(True)
    __aliases_emoji_font.setPointSize(13)
    __line_edit_font = QFont()
    __line_edit_font.setPointSize(12)

    def __init__(self, favorite_category: bool = True, recent_category: bool = True):
        super().__init__()
        self.__favorite_category = favorite_category
        self.__recent_category = recent_category
        self.__line_edit = QLineEdit()
        self.__line_edit.setFont(self.__line_edit_font)
        self.__line_edit.setPlaceholderText(
            translate("QEmojiPicker", "Enter your favorite emoji")
        )
        self.__categories = {}
        self.__emoji_label = QLabel()
        self.__emoji_label.setFixedSize(QSize(32, 32))
        self.__emoji_label.setScaledContents(True)
        self.__aliases_emoji_label = QLabel()
        self.__aliases_emoji_label.setFont(self.__aliases_emoji_font)
        self.__menu_horizontal_layout = QHBoxLayout()
        self.__scroll_area = QScrollArea()
        self.__scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        self.__collapse_groups_layout = QVBoxLayout(content_widget)
        self.__scroll_area.setWidget(content_widget)
        self.__emoji_layout = QHBoxLayout()
        self.__emoji_layout.addWidget(self.__emoji_label)
        self.__emoji_layout.addWidget(self.__aliases_emoji_label)
        self.__emoji_layout.setStretch(1, True)
        self.__vertical_layout = QVBoxLayout()
        self.__vertical_layout.addLayout(self.__menu_horizontal_layout)
        self.__vertical_layout.addWidget(self.__line_edit)
        self.__vertical_layout.addWidget(self.__scroll_area)
        self.__vertical_layout.addLayout(self.__emoji_layout)
        self.setLayout(self.__vertical_layout)
        self.__add_categories()
        self.__load_emojis()
        self.__hide_empty_categories()
        self.__bind_signals()

    def __bind_signals(self):
        self.__line_edit.textEdited.connect(lambda: self.__filter_emojis(self.__line_edit.text()))
        self.__line_edit.textEdited.connect(lambda: QTimer.singleShot(5, self.__hide_empty_categories))

        if self.__favorite_category:
            self.favorite.connect(lambda emoji: self.add_favorite(emoji))
            self.favorite.connect(lambda: self.__filter_emojis(self.__line_edit.text()))
            self.favorite.connect(lambda: QTimer.singleShot(5, self.__hide_empty_categories))
            self.removed_favorite.connect(lambda emoji: self.remove_favorite(emoji))
            self.removed_favorite.connect(lambda: self.__filter_emojis(self.__line_edit.text()))
            self.removed_favorite.connect(lambda: QTimer.singleShot(5, self.__hide_empty_categories))

    def __add_categories(self):
        if self.__recent_category:
            self.add_category(
                "Recent",
                get_awesome_icon("clock-rotate-left"),
                translate("QEmojiPicker", "Recent"),
            )
        if self.__favorite_category:
            self.add_category(
                "Favorite",
                get_awesome_icon("star"),
                translate("QEmojiPicker", "Favorite"),
            )
        self.add_category(
            "Smileys & Emotion",
            get_awesome_icon("face-smile"),
            translate("QEmojiPicker", "Smileys & Emotion"),
        )
        self.add_category(
            "Animals & Nature",
            get_awesome_icon("leaf"),
            translate("QEmojiPicker", "Animals & Nature"),
        )
        self.add_category(
            "Food & Drink",
            get_awesome_icon("bowl-food"),
            translate("QEmojiPicker", "Food & Drink"),
        )
        self.add_category(
            "Activities",
            get_awesome_icon("gamepad"),
            translate("QEmojiPicker", "Activities"),
        )
        self.add_category(
            "Travel & Places",
            get_awesome_icon("bicycle"),
            translate("QEmojiPicker", "Travel & Places"),
        )
        self.add_category(
            "Objects",
            get_awesome_icon("lightbulb"),
            translate("QEmojiPicker", "Objects"),
        )
        self.add_category(
            "Symbols",
            get_awesome_icon("heart"),
            translate("QEmojiPicker", "Symbols"),
        )
        self.add_category(
            "Flags",
            get_awesome_icon("flag"),
            translate("QEmojiPicker", "Flags"),
        )

    def __load_emojis(self):
        for category in self.__categories.keys():
            if category not in ("Favorite", "Recent"):
                self.__add_emojis(category, get_emojis_by_category(category))
        self.__add_emojis("Smileys & Emotion", get_emojis_by_category("People & Body"))

    def add_category(self, category: str, icon: QIcon, title: str):
        shortcut_button = QThemeResponsiveButton()
        shortcut_button.setFixedSize(QSize(30, 30))
        shortcut_button.setIconSize(QSize(22, 22))
        shortcut_button.setFlat(True)
        shortcut_button.setIcon(icon)
        shortcut_button.clicked.connect(lambda: self.__on_shortcut_click(category))
        self.__menu_horizontal_layout.addWidget(shortcut_button)
        collapse_group = QCollapseGroup(title, QEmojiGrid())
        self.__categories[category] = {
            "shortcut": shortcut_button,
            "group": collapse_group,
        }
        self.__collapse_groups_layout.addWidget(collapse_group)

    def __collapse_all_but(self, category: str):
        for category_2 in self.__categories.keys():
            self.collapse_group(category_2).set_collapse(category_2 != category)

    def __scroll_to_category(self, category: str):
        self.__scroll_area.verticalScrollBar().setValue(
            self.collapse_group(category).y()
        )

    def __on_shortcut_click(self, category: str):
        self.__collapse_all_but(category)
        QTimer.singleShot(5, lambda: self.__scroll_to_category(category))

    def collapse_group(self, category: str) -> QCollapseGroup:
        return self.__categories[category]["group"]

    def emoji_grid(self, category: str) -> QEmojiGrid:
        return self.__categories[category]["group"].widget()

    def shortcut(self, category: str) -> QThemeResponsiveButton:
        return self.__categories[category]["shortcut"]

    def __add_emojis(self, category: str, emojis_: typing.List[Emoji]):
        for emoji in emojis_:
            self.__add_emoji(category, emoji)

    def __add_emoji(self, category: str, emoji: Emoji) -> QEmojiButton:
        emoji_grid = self.emoji_grid(category)
        emoji_button = QEmojiButton(emoji)
        self.__bind_emoji_button(emoji_button)
        emoji_grid.add_emoji(emoji_button)
        return emoji_button

    def __remove_emoji(self, category: str, emoji: Emoji):
        emoji_grid = self.emoji_grid(category)
        emoji_button = emoji_grid.get_emoji(emoji)
        emoji_button.deleteLater()
        emoji_grid.update()

    def __bind_emoji_button(self, emoji_button: QEmojiButton):
        emoji = emoji_button.emoji()
        emoji_button.enterEvent = lambda event: self.__set_emoji_label(emoji)
        emoji_button.leaveEvent = lambda event: self.__mouse_leave_emoji()
        if self.__favorite_category:
            emoji_button.setContextMenuPolicy(
                Qt.ContextMenuPolicy.CustomContextMenu
            )
            emoji_button.customContextMenuRequested.connect(
                lambda position: self.__open_button_context_menu(position, emoji_button)
            )
        emoji_button.clicked.connect(lambda: self.picked.emit(emoji))
        if self.__recent_category:
            emoji_button.clicked.connect(lambda: self.__add_recent(emoji))
            emoji_button.clicked.connect(lambda: self.__filter_emojis(self.__line_edit.text()))
            emoji_button.clicked.connect(lambda: QTimer.singleShot(5, self.__hide_empty_categories))

    def add_recent(self, emoji: Emoji):
        if not self.__recent_category:
            raise RecentNotImplemented()

        if self.is_recent(emoji):
            raise EmojiAlreadyExists(emoji.emoji)

        self.__add_emoji("Recent", emoji)
        self.emoji_grid("Recent").filter(self.__line_edit.text())

    def __add_recent(self, emoji: Emoji):
        with contextlib.suppress(EmojiAlreadyExists):
            self.add_recent(emoji)

    def is_recent(self, emoji: Emoji) -> bool:
        if not self.__recent_category:
            raise RecentNotImplemented()

        emoji_grid = self.emoji_grid("Recent")
        return bool(emoji_grid.get_emoji(emoji))

    def remove_recent(self, emoji: Emoji):
        if not self.__recent_category:
            raise RecentNotImplemented()

        self.__remove_emoji("Recent", emoji)

    def add_favorite(self, emoji: Emoji):
        if not self.__favorite_category:
            raise FavoriteNotImplemented()

        if self.is_favorite(emoji):
            raise EmojiAlreadyExists(emoji.emoji)

        self.__add_emoji("Favorite", emoji)

    def is_favorite(self, emoji: Emoji) -> bool:
        if not self.__favorite_category:
            raise FavoriteNotImplemented()

        emoji_grid = self.emoji_grid("Favorite")
        return bool(emoji_grid.get_emoji(emoji))

    def remove_favorite(self, emoji: Emoji):
        if not self.__favorite_category:
            raise FavoriteNotImplemented()

        self.__remove_emoji("Favorite", emoji)

    def emoji_button(self, emoji: Emoji) -> typing.Optional[QEmojiButton]:
        for category in self.__categories.keys():
            if category not in ("Favorite", "Recent"):
                emoji_grid = self.emoji_grid(category)
                emoji_button = emoji_grid.get_emoji(emoji)
                if emoji_button:
                    return emoji_button

    def __set_emoji_label(self, emoji: Emoji):
        aliases = " ".join(map(lambda alias: f":{alias}:", emoji.aliases))
        self.__emoji_label.setPixmap(QPixmap(get_emoji_path(emoji)))
        self.__aliases_emoji_label.setText(aliases)

    def __hide_empty_categories(self):
        for category in self.__categories.keys():
            emoji_grid = self.emoji_grid(category)
            is_empty = emoji_grid.is_empty()
            collapse_group = self.collapse_group(category)
            collapse_group.setHidden(is_empty or emoji_grid.all_hidden())
            shortcut = self.shortcut(category)
            shortcut.setHidden(is_empty)

    def __filter_emojis(self, emoji_alias: str = ""):
        for category in self.__categories.keys():
            emoji_grid = self.emoji_grid(category)
            emoji_grid.filter(emoji_alias)

    def __mouse_leave_emoji(self):
        self.__emoji_label.clear()
        self.__aliases_emoji_label.clear()

    def reset(self):
        self.__line_edit.clear()
        self.__filter_emojis()
        self.__scroll_area.verticalScrollBar().setValue(0)

    def __open_button_context_menu(self, position: QPoint, button: QEmojiButton):
        context_menu = QMenu()
        emoji = button.emoji()
        if self.is_favorite(emoji):
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