import sys

from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout
from emojis.db import Emoji

from qextrawidgets.documents.twemoji_text_document import QTwemojiTextDocument
from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.widgets.emoji_picker.emoji_picker import QEmojiPicker
from qextrawidgets.widgets.extra_text_edit import QExtraTextEdit


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QEmojiPicker Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        widget = QWidget()

        text_edit = QExtraTextEdit()
        document: QTwemojiTextDocument = text_edit.document()
        document.setLineLimit(1)

        emoji_picker = QEmojiPicker()
        emoji_picker.picked.connect(lambda emoji: text_edit.insertPlainText(Emoji(*emoji).emoji))

        # center line_edit on widget
        layout = QVBoxLayout()

        layout.addWidget(emoji_picker)
        layout.addWidget(text_edit)
        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
