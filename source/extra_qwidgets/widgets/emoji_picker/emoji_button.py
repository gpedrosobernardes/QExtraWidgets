from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QPushButton
from emojis.db import Emoji

from source.extra_qwidgets.utils import get_emoji_path


class QEmojiButton(QPushButton):
    font = QFont()
    font.setPointSize(20)

    def __init__(self, emoji: Emoji):
        super().__init__()
        self.__emoji = emoji
        self.setIcon(QIcon(get_emoji_path(emoji)))
        self.setFixedSize(QSize(40, 40))
        self.setIconSize(QSize(36, 36))
        self.setStyleSheet("padding: 0; background-color: transparent;")
        self.setFlat(True)

    def emoji(self) -> Emoji:
        return self.__emoji

    def has_in_aliases(self, emoji_alias: str) -> bool:
        return any(
            emoji_alias in emoji_alias_2 for emoji_alias_2 in self.__emoji.aliases
        )