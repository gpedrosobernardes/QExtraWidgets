import typing

from PySide6.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget


class QResponsiveTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__maximum_height = None
        self.__adjust_height()
        self.textChanged.connect(self.__adjust_height)

    def __adjust_height(self):
        height = (
            int(self.document().size().height())
            + self.contentsMargins().top()
            + self.contentsMargins().bottom()
        )
        maxh = self.maximumHeight()
        if maxh is None:
            self.setFixedHeight(height)
        elif height <= maxh:
            self.setFixedHeight(height)
        else:
            self.setFixedHeight(self.maximumHeight())

    def maximumHeight(self) -> typing.Optional[int]:
        return self.__maximum_height

    def setMaximumHeight(self, maxh: typing.Optional[int]):
        self.__maximum_height = maxh

    def resizeEvent(self, e):
        self.__adjust_height()
        super().resizeEvent(e)

    def insertFromMimeData(self, source):
        super().insertFromMimeData(source)
        self.__adjust_height()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTextEdit Auto-ajustável")

        self.text_edit = QResponsiveTextEdit()
        self.text_edit.setPlaceholderText("Digite algo...")
        # self.text_edit.setMaximumHeight(500)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
