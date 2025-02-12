import typing

from PySide6.QtWidgets import QTextEdit


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
