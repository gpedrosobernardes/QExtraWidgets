from PySide6.QtCore import QRegularExpression


class QEmojiColorRegex(QRegularExpression):
    def __init__(self):
        super().__init__(R"[\x{1F3FB}-\x{1F3FF}]")