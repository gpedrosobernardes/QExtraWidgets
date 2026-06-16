import typing

from PySide6.QtCore import QSize, Signal, QRunnable, QObject
from PySide6.QtGui import QImage
from emoji_data_python import EmojiChar

from qextrawidgets.core.utils.images import QIconGenerator


class QEmojiImageProvider(QRunnable):

    class Signals(QObject):
        imagesReady = Signal(str, QImage)

    def __init__(self, emoji_char: EmojiChar, size: QSize, font_family: str):
        super().__init__()
        self._emoji_char = emoji_char
        self._size = size
        self._font_family = font_family
        self.__signals = self.Signals()
        self.imagesReady = self.__signals.imagesReady


    def run(self):
        image = QIconGenerator.charToImageViaScan(self._emoji_char.char, self._size, self._font_family)
        self.imagesReady.emit(self._emoji_char.char, image)