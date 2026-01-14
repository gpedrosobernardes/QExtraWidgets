import sys

from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QLineEdit

from qextrawidgets.emoji_utils import EmojiImageProvider
from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.utils import QEmojiFonts
from qextrawidgets.widgets.emoji_picker.emoji_picker import QEmojiPicker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QEmojiPicker Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        widget = QWidget()

        font = QEmojiFonts.twemojiFont()

        line_edit = QLineEdit()
        line_edit.setFont(font)

        emoji_picker = QEmojiPicker()
        emoji_picker.picked.connect(lambda emoji: line_edit.insert(emoji))

        emoji_picker.setEmojiPixmapGetter(lambda emoji, size, dpr: EmojiImageProvider.getPixmap(emoji, 0, size, dpr))

        # center line_edit on widget
        layout = QVBoxLayout()

        layout.addWidget(emoji_picker)
        layout.addWidget(line_edit)
        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
