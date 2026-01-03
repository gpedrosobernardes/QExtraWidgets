from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QValidator

from qextrawidgets.emoji_utils import EmojiFinder


class QEmojiValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Allow one or more emojis from start to end
        emoji_pattern = EmojiFinder.get_emoji_pattern()
        self._re = QRegularExpression(
            f"^(?:{emoji_pattern})+$",
            QRegularExpression.PatternOption.UseUnicodePropertiesOption
        )

    def validate(self, input_str: str, pos: int):
        # Allow empty string
        if not input_str:
            return QValidator.State.Acceptable, input_str, pos

        match = self._re.match(input_str)
        if match.hasMatch():
            return QValidator.State.Acceptable, input_str, pos
        else:
            return QValidator.State.Invalid, input_str, pos
