from PySide6.QtGui import QValidator
from emoji import purely_emoji


class QEmojiValidator(QValidator):
    def validate(self, input_str: str, pos: int):
        if purely_emoji(input_str):
            return QValidator.State.Acceptable, input_str, pos
        else:
            return QValidator.State.Invalid, input_str, pos
