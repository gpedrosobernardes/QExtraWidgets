from encodings.cp862 import encoding_map
from ipaddress import collapse_addresses
import emojis.db
from PySide6 import QtCore
from PySide6.QtCore import QEvent
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QLabel, QGridLayout, QVBoxLayout, QPushButton, \
    QScrollArea
from emojis.db import Emoji
from utils import is_dark_mode, colorize_icon


class QColorResponsiveButton(QPushButton):
    def __init__(self, parent=None):
        super(QColorResponsiveButton, self).__init__(parent)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.PaletteChange:
            self.setIcon(self.icon())
        return super().eventFilter(obj, event)

    def setIcon(self, icon):
        if is_dark_mode():
            icon = colorize_icon(icon, "#FFFFFF")
        super().setIcon(icon)


class QCollapseGroup(QWidget):
    def __init__(self, title: str, widget: QWidget):
        super().__init__()
        self.__collapsed = False
        self.__widget = widget
        self.__collapse_button = QColorResponsiveButton()
        self.__collapse_button.setIcon(QIcon("assets/icons/angle-down-solid.svg"))
        self.__collapse_button.setFlat(True)
        self.__collapse_button.clicked.connect(lambda: self.set_collapse(not self.__collapsed))
        self.__label = QLabel(title)
        self.__header_layout = QHBoxLayout()
        self.__header_layout.addWidget(self.__collapse_button)
        self.__header_layout.addWidget(self.__label)
        self.__header_layout.setStretch(1, True)
        self.__layout = QVBoxLayout()
        self.__layout.addLayout(self.__header_layout)
        self.__layout.addWidget(widget)
        self.setLayout(self.__layout)

    def set_collapse(self, collapse: bool):
        if collapse:
            self.__widget.hide()
            self.__collapse_button.setIcon(QIcon("assets/icons/angle-right-solid.svg"))
        else:
            self.__widget.show()
            self.__collapse_button.setIcon(QIcon("assets/icons/angle-down-solid.svg"))
        self.__collapsed = collapse

    def widget(self):
        return self.__widget

    def header(self) -> QLabel:
        return self.__label


class QEmojiButton(QPushButton):
    font = QFont()
    font.setPointSize(20)

    def __init__(self, emoji: Emoji):
        super().__init__(emoji.emoji)
        self.__emoji = emoji
        self.setStyleSheet("padding: 0; background-color: transparent;")
        self.setFlat(True)
        self.setFont(self.font)

    def emoji(self) -> Emoji:
        return self.__emoji

    def has_in_aliases(self, emoji_alias: str) -> bool:
        for emoji_alias_2 in self.__emoji.aliases:
            if emoji_alias in emoji_alias_2:
                return True
        return False


class QEmojiGrid(QWidget):
    def __init__(self):
        super().__init__()
        self.__hidden_emojis = []
        self.__grid_layout = QGridLayout()
        self.__grid_layout.setSpacing(0)
        self.setLayout(self.__grid_layout)

    def add_emoji(self, emoji: Emoji, enter_callback = None, leave_callback = None):
        button = QEmojiButton(emoji)
        button.enterEvent = lambda event: enter_callback(emoji)
        button.leaveEvent = lambda event: leave_callback()
        self.__grid_layout.addWidget(button, *self.__next_position(self.layout().count()))

    def emojis(self) -> list[QEmojiButton]:
        return list(filter(lambda emoji_button: isinstance(emoji_button, QEmojiButton), self.children()))

    def all_hidden(self) -> bool:
        return len(self.__hidden_emojis) == len(self.emojis())

    def filter(self, emoji_alias: str):
        removed = 0
        all_emojis = self.emojis()
        for index, emoji_button in enumerate(all_emojis):
            if emoji_button.has_in_aliases(emoji_alias):
                if emoji_button in self.__hidden_emojis:
                    self.__hidden_emojis.remove(emoji_button)
                    emoji_button.show()
                else:
                    self.__grid_layout.removeWidget(emoji_button)
                position = self.__next_position(index - removed)
                self.__grid_layout.addWidget(emoji_button, *position)
            else:
                if emoji_button not in self.__hidden_emojis:
                    self.__grid_layout.removeWidget(emoji_button)
                    emoji_button.hide()
                    self.__hidden_emojis.append(emoji_button)
                removed += 1
        self.__grid_layout.update()
        self.update()

    @staticmethod
    def __next_position(index: int) -> tuple[int, int]:
        return index // 9, index % 9


class QEmojiPicker(QWidget):
    bottom_font = QFont()
    bottom_font.setBold(True)
    bottom_font.setPointSize(16)
    line_edit_font = QFont()
    line_edit_font.setPointSize(12)

    def __init__(self):
        super().__init__()
        self.__line_edit = QLineEdit()
        self.__line_edit.setFont(self.line_edit_font)
        self.__line_edit.setPlaceholderText("Enter your favorite emoji")
        self.__line_edit.textEdited.connect(self.__line_edited)
        self.__categories = {}
        self.__current_emoji_label = QLabel()
        self.__current_emoji_label.setFont(self.bottom_font)
        self.__menu_horizontal_layout = QHBoxLayout()
        self.__scroll_area = QScrollArea()
        self.__scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        self.__collapse_groups_layout = QVBoxLayout(content_widget)
        self.__scroll_area.setWidget(content_widget)
        self.__vertical_layout = QVBoxLayout()
        self.__vertical_layout.addLayout(self.__menu_horizontal_layout)
        self.__vertical_layout.addWidget(self.__line_edit)
        self.__vertical_layout.addWidget(self.__scroll_area)
        self.__vertical_layout.addWidget(self.__current_emoji_label)
        self.setLayout(self.__vertical_layout)
        self.add_category("Smileys & Emotion", QIcon("assets/icons/face-smile-solid.svg"))
        self.__insert_emojis("Smileys & Emotion")
        self.add_category("Animals & Nature", QIcon("assets/icons/leaf-solid.svg"))
        self.__insert_emojis("Animals & Nature")
        self.add_category("Food & Drink", QIcon("assets/icons/bowl-food-solid.svg"))
        self.__insert_emojis("Food & Drink")
        self.add_category("Activities", QIcon("assets/icons/gamepad-solid.svg"))
        self.__insert_emojis("Activities")
        self.add_category('Travel & Places', QIcon("assets/icons/bicycle-solid.svg"))
        self.__insert_emojis('Travel & Places')
        self.add_category('Objects', QIcon("assets/icons/lightbulb-solid.svg"))
        self.__insert_emojis('Objects')
        self.add_category("Symbols", QIcon("assets/icons/heart-solid.svg"))
        self.__insert_emojis('Symbols')
        self.add_category('Flags', QIcon("assets/icons/flag-solid.svg"))
        self.__insert_emojis("Flags")

    def add_category(self, category: str, icon: QIcon):
        shortcut_button = QColorResponsiveButton()
        shortcut_button.setFlat(True)
        shortcut_button.setIcon(icon)
        shortcut_button.clicked.connect(lambda: self.__collapse_all_but(category))
        shortcut_button.clicked.connect(lambda: self.__move_to_category(category))
        self.__menu_horizontal_layout.addWidget(shortcut_button)
        collapse_group = QCollapseGroup(category, QEmojiGrid())
        self.__categories[category] = {"shortcut": shortcut_button, "group": collapse_group}
        self.__collapse_groups_layout.addWidget(collapse_group)

    def __collapse_all_but(self, category: str):
        for category_2 in self.__categories.keys():
            if category_2 != category:
                self.collapse_group(category_2).set_collapse(True)
        self.collapse_group(category).set_collapse(False)

    def __move_to_category(self, category: str):
        collapse_group = self.collapse_group(category)
        self.__scroll_area.ensureWidgetVisible(collapse_group.header())

    def collapse_group(self, category: str) -> QCollapseGroup:
        return self.__categories[category]["group"]

    def emoji_grid(self, category: str) -> QEmojiGrid:
        return self.__categories[category]["group"].widget()

    def shortcut(self, category: str) -> QColorResponsiveButton:
        return self.__categories[category]["shortcut"]

    def __insert_emojis(self, category: str):
        emoji_grid = self.emoji_grid(category)
        for emoji in emojis.db.get_emojis_by_category(category):
            emoji_grid.add_emoji(emoji, self.__mouse_enter_emoji, self.__mouse_leave_emoji)

    def __mouse_enter_emoji(self, emoji: Emoji):
        aliases = " ".join(map(lambda alias: f":{alias}:", emoji.aliases))
        self.__current_emoji_label.setText(f"{emoji.emoji} {aliases}")

    def __line_edited(self):
        for category in self.__categories.keys():
            emoji_grid = self.emoji_grid(category)
            emoji_grid.filter(self.__line_edit.text())
            collapse_group = self.collapse_group(category)
            collapse_group.set_collapse(emoji_grid.all_hidden())

    def __mouse_leave_emoji(self):
        self.__current_emoji_label.clear()
