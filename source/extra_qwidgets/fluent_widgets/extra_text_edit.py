from qfluentwidgets import TextEdit

from extra_qwidgets.widgets.extra_text_edit import QExtraTextEdit


class ExtraTextEdit(TextEdit, QExtraTextEdit):
    def __init__(self, parent = None):
        super().__init__(parent)