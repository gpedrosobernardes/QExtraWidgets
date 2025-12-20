import sys

import qtawesome
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout
from emojis.db import Emoji
from qfluentwidgets import Theme, setTheme

from extra_qwidgets.documents.twemoji_text_document import QTwemojiTextDocument
from extra_qwidgets.fluent_widgets.emoji_picker.emoji_picker import EmojiPicker
from extra_qwidgets.fluent_widgets.extra_text_edit import ExtraTextEdit
from extra_qwidgets.utils import colorize_icon_by_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Emoji Picker Test")
        self.setWindowIcon(colorize_icon_by_theme(qtawesome.icon("fa6b.python")))

        widget = QWidget()

        text_edit = ExtraTextEdit()
        document: QTwemojiTextDocument = text_edit.document()
        document.setLineLimit(1)

        emoji_picker = EmojiPicker()
        emoji_picker.picked.connect(lambda emoji: text_edit.insertPlainText(Emoji(*emoji).emoji))

        # center line_edit on widget
        layout = QVBoxLayout()
        layout.addWidget(emoji_picker)
        layout.addWidget(text_edit)
        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    setTheme(Theme.AUTO)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
