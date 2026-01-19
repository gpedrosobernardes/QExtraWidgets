import typing

from PySide6.QtCore import QRegularExpression, QSize, QRegularExpressionMatch, QUrl, QUrlQuery
from PySide6.QtGui import QPixmap, QPixmapCache, QImageReader, Qt, QPainter
from twemoji_api.api import get_emoji_path
from emoji_data_python import unified_to_char, char_to_unified, find_by_shortname, find_by_name, EmojiChar


class EmojiFinder:
    """Utility class for finding emojis and aliases in text using QRegularExpression."""

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
        """Returns the raw regex pattern string for a single emoji.

        Returns:
            str: The regex pattern.
        """
        return cls._EMOJI_PATTERN

    @classmethod
    def getRegex(cls) -> QRegularExpression:
        """Returns a compiled QRegularExpression for finding emojis.

        Returns:
            QRegularExpression: The compiled regex.
        """
        return QRegularExpression(
            cls._EMOJI_PATTERN,
            QRegularExpression.PatternOption.UseUnicodePropertiesOption
        )

    @classmethod
    def findEmojis(cls, text: str) -> typing.Generator[QRegularExpressionMatch, None, None]:
        """Finds all Unicode emojis in the given text.

        Args:
            text (str): The text to scan.

        Yields:
            Generator[QRegularExpressionMatch]: Matches for each emoji found.
        """
        regex = cls.getRegex()
        iterator = regex.globalMatch(text)
        while iterator.hasNext():
            yield iterator.next()

    @classmethod
    def findEmojiAliases(cls, text: str) -> typing.Generator[typing.Tuple[EmojiChar, QRegularExpressionMatch], None, None]:
        """Finds all text aliases (e.g., :smile:) in the given text.

        Args:
            text (str): The text to scan.

        Yields:
            Generator[Tuple[EmojiChar, QRegularExpressionMatch]]: Tuples of EmojiChar data and their matches.
        """
        regex = QRegularExpression(cls._ALIAS_PATTERN)
        iterator = regex.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            first_captured = match.captured(0)
            alias = first_captured[1:-1]
            emoji = find_by_shortname(alias)
            if len(emoji) == 1:
                yield emoji[0], match


class EmojiImageProvider:
    """Utility class for loading, resizing, and caching emoji images."""

    @staticmethod
    def getPixmap(emoji: str, margin: int, size: QSize, dpr: float = 1.0, source_format: str = "png") -> QPixmap:
        """Loads and returns a colorized or processed emoji pixmap.

        Uses caching to improve performance on subsequent calls.

        Args:
            emoji (str): Emoji character.
            margin (int): Margin around the emoji in pixels.
            size (QSize): Target logical size.
            dpr (float, optional): Device pixel ratio. Defaults to 1.0.
            source_format (str, optional): Image format (png or svg). Defaults to "png".

        Returns:
            QPixmap: The processed pixmap.
        """

        # 1. Calculate real physical size (pixels)
        target_width = int(size.width() * dpr)
        target_height = int(size.height() * dpr)

        # 2. Generate unique key for Cache
        cache_url = EmojiImageProvider.getUrl(char_to_unified(emoji), margin, size, dpr, source_format)

        # 3. Try to fetch from Cache
        pixmap = QPixmap()
        if QPixmapCache.find(cache_url.toString(), pixmap):
            return pixmap

        # --- CACHE MISS (Load from disk) ---

        # 4. Load using QImageReader (more efficient than QPixmap(path))
        emoji_path = str(get_emoji_path(emoji, source_format))
        reader = QImageReader(emoji_path)

        if reader.canRead():
            # Important for SVG: Define render size before reading
            reader.setScaledSize(QSize(target_width, target_height))

            image = reader.read()
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                pixmap.setDevicePixelRatio(dpr)

                # Apply margin
                if margin > 0:
                    height = int((size.height() + (margin * 2)) * dpr)
                    width = int((size.width() + (margin * 2)) * dpr)
                    final_pixmap = QPixmap(width, height)
                    final_pixmap.setDevicePixelRatio(dpr)
                    final_pixmap.fill(Qt.GlobalColor.transparent)

                    painter = QPainter(final_pixmap)
                    painter.drawPixmap(margin, margin, pixmap)
                    painter.end()
                    pixmap = final_pixmap

                # Save to cache for future
                QPixmapCache.insert(cache_url.toString(), pixmap)
                return pixmap

        # 5. Fallback (Returns a transparent pixmap or placeholder in case of error)
        fallback = QPixmap(size * dpr)
        fallback.fill(Qt.GlobalColor.transparent)
        fallback.setDevicePixelRatio(dpr)
        return fallback

    @staticmethod
    def getUrl(alias: str, margin: int, size: QSize, dpr: float, source_format: str) -> QUrl:
        """Generates a unique QUrl key for caching an emoji pixmap.

        Args:
            alias (str): Emoji identifier (unified code or alias).
            margin (int): Margin size.
            size (QSize): Logical size.
            dpr (float): Device pixel ratio.
            source_format (str): Image format.

        Returns:
            QUrl: The generated cache key URL.
        """
        url = QUrl()
        url.setScheme("twemoji")
        url.setPath(alias)

        query_params = QUrlQuery()
        query_params.addQueryItem("margin", str(margin))
        query_params.addQueryItem("width", str(size.width()))
        query_params.addQueryItem("height", str(size.height()))
        query_params.addQueryItem("dpr", str(dpr))
        query_params.addQueryItem("source_format", source_format)

        url.setQuery(query_params)

        return url