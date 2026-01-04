import typing

from PySide6.QtCore import QRegularExpression, QSize, QRegularExpressionMatch
from PySide6.QtGui import QPixmap, QPixmapCache, QImageReader, Qt
from emojis.db import Emoji, get_emoji_by_alias, get_emoji_by_code
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

    _ALIAS_PATTERN = R"(:\w+:)"

    _COLOR_PATTERN = R"[\x{1F3FB}-\x{1F3FF}]"

    @classmethod
    def getEmojiPattern(cls) -> str:
        """Returns the raw regex pattern string for a single emoji."""
        return cls._EMOJI_PATTERN

    @classmethod
    def getRegex(cls) -> QRegularExpression:
        """Returns a compiled QRegularExpression for finding emojis."""
        return QRegularExpression(
            cls._EMOJI_PATTERN,
            QRegularExpression.PatternOption.UseUnicodePropertiesOption
        )

    @classmethod
    def findEmojis(cls, text: str) -> typing.Generator[QRegularExpressionMatch, None, None]:
        """
        Finds all emojis in the given text.
        Returns a generator of QRegularExpressionMatch objects.
        """
        regex = cls.getRegex()
        iterator = regex.globalMatch(text)
        while iterator.hasNext():
            yield iterator.next()

    @classmethod
    def findEmojiObjects(cls, text: str, ignore_colors: bool = False) -> typing.Generator[
        typing.Tuple[Emoji, QRegularExpressionMatch], None, None]:
        """
        Finds all emojis in the given text.
        Returns a generator of Emoji objects.
        """
        for match in cls.findEmojis(text):
            emoji_str = match.captured(0)
            if ignore_colors:
                for color_match in cls.findEmojiColors(emoji_str):
                    emoji_str = emoji_str.replace(color_match.captured(0), "")
            emoji = get_emoji_by_code(emoji_str)
            if emoji:
                yield emoji, match

    @classmethod
    def findAliases(cls, text: str) -> typing.Generator[QRegularExpressionMatch, None, None]:
        """
        Finds all aliases in the given text.
        Returns a generator of QRegularExpressionMatch objects.
        """
        regex = QRegularExpression(cls._ALIAS_PATTERN)
        iterator = regex.globalMatch(text)
        while iterator.hasNext():
            yield iterator.next()

    @classmethod
    def findEmojiAliases(cls, text: str) -> typing.Generator[typing.Tuple[Emoji, QRegularExpressionMatch], None, None]:
        """
        Finds all aliases in the given text.
        Returns a generator of QRegularExpressionMatch objects.
        """
        for match in cls.findAliases(text):
            first_captured = match.captured(0)
            alias = first_captured[1:-1]
            emoji = get_emoji_by_alias(alias)
            if emoji:
                yield emoji, match

    @classmethod
    def findEmojiColors(cls, text: str) -> typing.Generator[QRegularExpressionMatch, None, None]:
        re_color = QRegularExpression(cls._COLOR_PATTERN)
        iterator = re_color.globalMatch(text)
        while iterator.hasNext():
            yield iterator.next()


class EmojiImageProvider:
    """
    Class exclusively responsible for loading, resizing, and caching
    emoji images.
    """

    @staticmethod
    def getPixmap(emoji_data: Emoji, size: QSize, dpr: float = 1.0) -> QPixmap:
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
        cache_key = f"emoji_{emoji_alias}-{target_width}x{target_height}"

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
