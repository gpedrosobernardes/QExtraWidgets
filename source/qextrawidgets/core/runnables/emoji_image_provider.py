from PySide6.QtCore import QSize

from qextrawidgets.core.runnables.image_provider import QImageProvider
from qextrawidgets.core.utils.images import QIconGenerator


class QEmojiImageProvider(QImageProvider):
    def run(self):
        emoji = self._url_query.queryItemValue("emoji")
        size = int(self._url_query.queryItemValue("size"))
        font_family = self._url_query.queryItemValue("font_family")

        image = QIconGenerator.charToImage(emoji, QSize(size, size), font_family)
        self.success.emit(self._url_query, image)