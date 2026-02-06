import typing
from PySide6.QtCore import QObject
from PySide6.QtGui import QRegularExpressionValidator

from qextrawidgets.core.regexes.emoji_regex import QEmojiRegex


class QEmojiValidator(QRegularExpressionValidator):
    """A validator that only accepts text consisting exclusively of emojis."""

    def __init__(self, parent: typing.Optional[QObject] = None) -> None:
        """Initializes the emoji validator.

        Args:
            parent (QObject, optional): Parent object. Defaults to None.
        """
        super().__init__(QEmojiRegex(), parent)