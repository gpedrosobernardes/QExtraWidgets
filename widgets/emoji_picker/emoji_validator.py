from PySide6.QtGui import QValidator
from emojis import emojis


class QEmojiValidator(QValidator):
    def validate(self, input_str: str, pos: int):
        if emojis.count(input_str) == len(input_str):
            return QValidator.State.Acceptable, input_str, pos
        else:
            return QValidator.State.Invalid, input_str, pos
