import logging
import sys

import qtawesome
from PySide6.QtWidgets import QMainWindow, QApplication, QLineEdit, QWidget, QVBoxLayout
from qfluentwidgets import Theme, setTheme

from extra_qwidgets.fluent_widgets.emoji_picker.emoji_picker import EmojiPicker
from extra_qwidgets.utils import colorize_icon_by_theme
from extra_qwidgets.validators.emoji_validator import QEmojiValidator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Emoji Picker Test")
        self.setWindowIcon(colorize_icon_by_theme(qtawesome.icon("fa6b.python")))

        widget = QWidget()

        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Enter your favorite emoji")
        line_edit.setValidator(QEmojiValidator())

        emoji_picker = EmojiPicker()
        emoji_picker.picked.connect(lambda emoji: line_edit.insert(emoji.emoji))

        # center line_edit on widget
        layout = QVBoxLayout()
        layout.addWidget(line_edit)
        layout.addWidget(emoji_picker)
        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    setTheme(Theme.AUTO)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
