from PySide6.QtCore import QStandardPaths, QDir, QSize
from PySide6.QtGui import QFont, QPainter, QPixmap, QFontMetrics, Qt, QImage
from emoji_data_python import EmojiChar

from qextrawidgets.core.utils.emojis.emoji_utils import QEmojiUtils
from qextrawidgets.core.utils.system_utils import log_qt_performance


class QEmojiPixmapCache:
    pixmapSize = 128

    def __init__(self, font_family: str):
        self._font = QFont(font_family)
        self._font.setPixelSize(self.pixmapSize)
        self._font_metrics = QFontMetrics(self._font)

        self._cache = {}

        self._dir = QDir(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation))

        if not self._dir.exists("emojis"):
            self._dir.mkpath("emojis")
            self._dir.cd("emojis")

        file = f"{font_family}.pack"

        if self._dir.exists(file):
            self._load_font_cache()
        else:
            self._cache_font()

    def _create_char_image(self, char: str) -> QImage:
        bounding_rect = self._font_metrics.boundingRect(char)

        image = QImage(bounding_rect.width(), bounding_rect.height(), QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        painter.setFont(self._font)
        painter.drawText(
            image.rect(),
            Qt.AlignmentFlag.AlignCenter,
            char
        )
        painter.end()

        image = image.scaled(QSize(self.pixmapSize, self.pixmapSize), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        return image

    @log_qt_performance
    def _cache_font(self):
        for emoji_char in QEmojiUtils.getAllEmojiChars():
            self._cache_emoji_char_pixmap(emoji_char)

    def _cache_emoji_char_pixmap(self, emoji_char: EmojiChar):
        base_pixmap = self._create_char_pixmap(emoji_char.char)
        self._cache[emoji_char.char] = base_pixmap
        base_pixmap.save(self._dir.filePath(emoji_char.image))

    @log_qt_performance
    def _load_font_cache(self):
        for emoji_char in QEmojiUtils.getAllEmojiChars():
            self._load_emoji_char_pixmap(emoji_char)

    # @log_qt_performance
    def _load_emoji_char_pixmap(self, emoji_char: EmojiChar):
        file_path = self._dir.filePath(emoji_char.image)
        pixmap = QPixmap(file_path)
        self._cache[emoji_char.char] = pixmap

    def getPixmap(self, char: str) -> QPixmap:
        return self._cache[char]