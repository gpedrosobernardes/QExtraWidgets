from PySide6.QtCore import QRegularExpression, QObject
from PySide6.QtGui import QRegularExpressionValidator

from qextrawidgets.core.regexes.emoji_regex import QEmojiRegex
from qextrawidgets.core.utils.emoji_finder import QEmojiFinder


class QEmojiValidator(QRegularExpressionValidator):
    """A validator that only accepts text consisting exclusively of emojis."""

    def __init__(self, parent: QObject = None) -> None:
        """Initializes the emoji validator.

        Args:
            parent (QObject, optional): Parent object. Defaults to None.
        """
        super().__init__(QEmojiRegex(), parent)