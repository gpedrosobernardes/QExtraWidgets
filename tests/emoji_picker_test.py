import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QApplication, QLineEdit, QWidget, QVBoxLayout

from widgets.emoji_picker.emoji_picker import QEmojiPicker
from widgets.utils import colorize_icon, get_icon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Emoji Picker Test")
        self.setWindowIcon(colorize_icon(get_icon("python-brands-solid.svg"), "#FFFFFF"))

        widget = QWidget()

        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Enter your favorite emoji")

        emoji_picker = QEmojiPicker()
        emoji_picker.picked.connect(lambda emoji: line_edit.insert(emoji.emoji))

        # center line_edit on widget
        layout = QVBoxLayout()
        layout.addWidget(line_edit)
        layout.addWidget(emoji_picker)
        widget.setLayout(layout)

        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
