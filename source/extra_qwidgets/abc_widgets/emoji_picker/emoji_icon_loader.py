from PySide6.QtCore import QObject, Signal, Slot, QSize
from PySide6.QtGui import QImageReader, QPixmap
from emojis.db import Emoji, get_emojis_by_category, get_categories

from extra_qwidgets.utils import get_emoji_path


class IconLoader(QObject):
    icon_loaded = Signal(Emoji, QPixmap)
    finished = Signal()

    def __init__(self):
        super().__init__()

    @Slot()
    def run(self):
        for category in get_categories():
            for emoji in get_emojis_by_category(category):
                reader = QImageReader(get_emoji_path(emoji))
                reader.setScaledSize(QSize(64, 64))
                if reader.canRead():
                    image = reader.read()
                    pixmap = QPixmap.fromImage(image)
                    self.icon_loaded.emit(emoji, pixmap)
        self.finished.emit()