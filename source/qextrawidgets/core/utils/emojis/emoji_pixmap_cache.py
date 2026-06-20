import struct

from PySide6.QtCore import QStandardPaths, QDir, QSize, QBuffer, QIODevice, QDataStream, QByteArray
from PySide6.QtGui import QFont, QPainter, QPixmap, QFontMetrics, Qt, QImage, QPixmapCache

from qextrawidgets.core.utils.emojis.emoji_utils import QEmojiUtils
from qextrawidgets.core.utils.system_utils import debug


class QEmojiPixmapCache:
    _caches: dict[str, dict[str, QPixmap]] = {}

    @classmethod
    def createCache(cls, font_family: str, force: bool = True):
        font = QFont(font_family)
        font.setPixelSize(128)
        font_metrics = QFontMetrics(font)

        cache_folder = QDir(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation))

        if not cache_folder.exists("emojis"):
            cache_folder.mkpath("emojis")

        cache_folder.cd("emojis")
        file_name = f"{font_family}.pack"

        if cache_folder.exists(file_name) and not force:
            raise ValueError("Cache file already exists!")

        file = cache_folder.absoluteFilePath(file_name)
        cls._create_font_cache_file(font_metrics, font, file)

    @debug
    @staticmethod
    def _create_char_image(font_metrics: QFontMetrics, font: QFont, char: str, **kwargs) -> QImage:
        bounding_rect = font_metrics.boundingRect(char)

        image = QImage(bounding_rect.width(), bounding_rect.height(), QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        painter.setFont(font)
        painter.drawText(
            image.rect(),
            Qt.AlignmentFlag.AlignCenter,
            char
        )
        painter.end()

        image = image.scaled(QSize(128, 128), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        return image

    @debug
    @staticmethod
    def _create_font_cache_file(font_metrics: QFontMetrics, font: QFont, file: str, **kwargs):
        # 1. Serializa cada QImage para bytes
        blobs: dict[str, bytes] = {}
        for emoji_char in QEmojiUtils.getAllEmojiChars():
            buf = QBuffer()
            buf.open(QIODevice.OpenModeFlag.WriteOnly)
            image = QEmojiPixmapCache._create_char_image(font_metrics, font, emoji_char.char)
            image.save(buf, "PNG")
            blobs[emoji_char.unified] = bytes(buf.data())

        # 3. Escreve o arquivo
        with open(file, "wb") as f:
            f.write(struct.pack(">I", len(blobs)))
            for codepoint, blob in blobs.items():
                cp_bytes = codepoint.encode()
                f.write(struct.pack(">IQ", len(cp_bytes), len(blob)))
                f.write(cp_bytes)
                f.write(blob)  # dado logo após sua entrada

    @classmethod
    @debug
    def loadCache(cls, font_family: str, **kwargs):
        cls._caches[font_family] = {}
        cache_folder = QDir(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation))
        cache_folder.cd("emojis")
        file = cache_folder.absoluteFilePath(f"{font_family}.pack")

        if not cache_folder.exists(file):
            raise ValueError("Font family cache doesn't exist!")

        with open(file, "rb") as f:
            count = struct.unpack(">I", f.read(4))[0]

            for _ in range(count):
                cp_len, blob_len = struct.unpack(">IQ", f.read(12))

                cp = f.read(cp_len).decode()
                blob = f.read(blob_len)

                buf = QBuffer(QByteArray(blob))
                buf.open(QIODevice.OpenModeFlag.ReadOnly)
                image = QImage()
                image.loadFromData(blob)
                cls._caches[font_family][cp] = QPixmap.fromImage(image)

    @classmethod
    def isCacheLoaded(cls, font_family: str):
        return font_family in cls._caches

    @classmethod
    def cacheExists(cls, font_family: str):
        cache_folder = QDir(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation))
        cache_folder.cd("emojis")
        file = cache_folder.absoluteFilePath(f"{font_family}.pack")
        return cache_folder.exists(file)

    @classmethod
    def ensureCacheLoaded(cls, font_family: str):
        if not cls.cacheExists(font_family):
            cls.createCache(font_family)

        cls.loadCache(font_family)

    @classmethod
    def getPixmap(cls, font_family: str, codepoint: str):
        return cls._caches[font_family][codepoint]