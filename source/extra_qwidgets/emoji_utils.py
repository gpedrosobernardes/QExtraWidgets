from PySide6.QtCore import QRegularExpression, QSize
from PySide6.QtGui import QPixmap, QPixmapCache, QImageReader, Qt
from emojis.db import Emoji
from twemoji_api.api import get_emoji_path


class EmojiFinder:
    """
    Utility class for finding emojis in text using PySide6's QRegularExpression.
    Centralizes the regex pattern logic used across the library.
    """
    
    # Regex pattern for a single emoji (based on unicode.org specs)
    # Covers: Tag sequences, Keycap sequences, Regional indicator sequences, Extended Pictographic sequences
    _EMOJI_PATTERN = (
        R"(?:\x{1F3F4}(?:\x{E0067}\x{E0062}\x{E0065}\x{E006E}\x{E0067}|\x{E0067}\x{E0062}\x{E0073}\x{E0063}\x{E0074}|\x{E0067}\x{E0062}\x{E0077}\x{E006C}\x{E0073})\x{E007F})|"
        R"(?:[\x{0030}-\x{0039}\x{0023}\x{002A}]\x{FE0F}?\x{20E3})|"
        R"(?:[\x{1F1E6}-\x{1F1FF}]{2})|"
        R"(?:\p{Extended_Pictographic}\x{FE0F}?(?:[\x{1F3FB}-\x{1F3FF}])?(?:\x{200D}\p{Extended_Pictographic}\x{FE0F}?(?:[\x{1F3FB}-\x{1F3FF}])?)*)"
    )

    @classmethod
    def get_emoji_pattern(cls) -> str:
        """Returns the raw regex pattern string for a single emoji."""
        return cls._EMOJI_PATTERN

    @classmethod
    def get_regex(cls) -> QRegularExpression:
        """Returns a compiled QRegularExpression for finding emojis."""
        return QRegularExpression(
            cls._EMOJI_PATTERN,
            QRegularExpression.PatternOption.UseUnicodePropertiesOption
        )

    @classmethod
    def find_all(cls, text: str):
        """
        Finds all emojis in the given text.
        Returns a list of QRegularExpressionMatch objects.
        """
        regex = cls.get_regex()
        iterator = regex.globalMatch(text)
        matches = []
        while iterator.hasNext():
            matches.append(iterator.next())
        return matches


class EmojiImageProvider:
    """
    Class exclusively responsible for loading, resizing, and caching
    emoji images.
    """

    @staticmethod
    def get_pixmap(emoji_data: Emoji, size: QSize, dpr: float = 1.0) -> QPixmap:
        """
        Returns a QPixmap ready to be drawn.

        :param emoji_data: Object containing the emoji path or code.
        :param size: Desired QSize (logical size).
        :param dpr: Device Pixel Ratio (for Retina/4K screens).
        """

        # 1. Calculate real physical size (pixels)
        target_width = int(size.width() * dpr)
        target_height = int(size.height() * dpr)

        # 2. Generate unique key for Cache
        emoji_alias = emoji_data[0][0]
        cache_key = f"emoji_{emoji_alias}"

        # 3. Try to fetch from Cache
        pixmap = QPixmap()
        if QPixmapCache.find(cache_key, pixmap):
            return pixmap

        # --- CACHE MISS (Load from disk) ---

        # 4. Load using QImageReader (more efficient than QPixmap(path))
        emoji_path = str(get_emoji_path(emoji_data[1]))
        reader = QImageReader(emoji_path)

        if reader.canRead():
            # Important for SVG: Define render size before reading
            reader.setScaledSize(QSize(target_width, target_height))

            image = reader.read()
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                pixmap.setDevicePixelRatio(dpr)

                # Save to cache for future
                QPixmapCache.insert(cache_key, pixmap)
                return pixmap

        # 5. Fallback (Returns a transparent pixmap or placeholder in case of error)
        fallback = QPixmap(size * dpr)
        fallback.fill(Qt.GlobalColor.transparent)
        fallback.setDevicePixelRatio(dpr)
        return fallback
