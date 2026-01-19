from PySide6.QtCore import QRegularExpression, QObject
from PySide6.QtGui import QRegularExpressionValidator
from qextrawidgets.emoji_utils import EmojiFinder


class QEmojiValidator(QRegularExpressionValidator):
    """A validator that only accepts text consisting exclusively of emojis."""

    def __init__(self, parent: QObject = None) -> None:
        """Initializes the emoji validator.

        Args:
            parent (QObject, optional): Parent object. Defaults to None.
        """
        emoji_pattern = EmojiFinder.getEmojiPattern()

        regex = QRegularExpression(
            f"^(?:{emoji_pattern})+$",
            QRegularExpression.PatternOption.UseUnicodePropertiesOption
        )

        super().__init__(regex, parent)