import qtawesome
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QPushButton

from extra_qwidgets.documents.twemoji_text_document import QTwemojiTextDocument
from extra_qwidgets.fluent_widgets.extra_text_edit import ExtraTextEdit

from source.extra_qwidgets.utils import colorize_icon_by_theme


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QTwemojiTextEdit Test")
        self.setWindowIcon(colorize_icon_by_theme(qtawesome.icon("fa6b.python")))

        self.text_edit = ExtraTextEdit()
        self.text_edit.setPlaceholderText("Digite algo...")
        self.text_edit.setMaximumHeight(500)

        self.document: QTwemojiTextDocument = self.text_edit.document()

        self.emojize_button = QPushButton("Emojize")
        self.demojize_button = QPushButton("Demojize")

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.emojize_button)
        layout.addWidget(self.demojize_button)

        self.emojize_button.pressed.connect(lambda: self.document.setTwemoji(True))
        self.demojize_button.pressed.connect(lambda: self.document.setTwemoji(False))

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()