import typing

from PySide6.QtWidgets import QGridLayout, QWidget
from emojis.db import Emoji

from source.extra_qwidgets.widgets.emoji_picker.emoji_button import QEmojiButton


class QEmojiGrid(QWidget):
    def __init__(self):
        super().__init__()
        self.__hidden_emojis = []
        self.__grid_layout = QGridLayout()
        self.__grid_layout.setSpacing(0)
        self.setLayout(self.__grid_layout)

    def add_emoji(self, emoji: QEmojiButton):
        self.__grid_layout.addWidget(emoji, *self.__next_position(self.layout().count()))

    def get_emoji(self, emoji: Emoji) -> typing.Optional[QEmojiButton]:
        for emoji_2 in self.emojis():
            if emoji_2.emoji() == emoji:
                return emoji_2

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