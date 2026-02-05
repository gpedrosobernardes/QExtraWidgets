from PySide6.QtCore import QSize, QUrl, QUrlQuery
from PySide6.QtGui import QPixmap, QPixmapCache, Qt, QImageReader, QPainter
from emoji_data_python import char_to_unified
from twemoji_api import get_emoji_path


class QTwemojiImageProvider:
    """Utility class for loading, resizing, and caching emoji images."""

    @staticmethod
    def getPixmap(emoji: str, margin: int, size: int, dpr: float = 1.0, source_format: str = "png") -> QPixmap:
        """Loads and returns a colorized or processed emoji pixmap.

        Uses caching to improve performance on subsequent calls.

        Args:
            emoji (str): Emoji character.
            margin (int): Margin around the emoji in pixels.
            size (int): Target logical size.
            dpr (float, optional): Device pixel ratio. Defaults to 1.0.
            source_format (str, optional): Image format (png or svg). Defaults to "png".

        Returns:
            QPixmap: The processed pixmap.
        """

        # 1. Calculate real physical size (pixels)
        target_size = int(size * dpr)

        # 2. Generate unique key for Cache
        cache_url = QTwemojiImageProvider.getUrl(char_to_unified(emoji), margin, size, dpr, source_format)

        # 3. Try to fetch from Cache
        pixmap = QPixmap()
        if QPixmapCache.find(cache_url.toString(), pixmap):
            return pixmap

        # --- CACHE MISS (Load from disk) ---

        # 4. Load using QImageReader (more efficient than QPixmap(path))
        emoji_path = str(get_emoji_path(emoji, source_format))
        if not emoji_path:
            # Fallback (Returns a transparent pixmap or placeholder in case of error)
            fallback = QPixmap(target_size, target_size)
            fallback.fill(Qt.GlobalColor.transparent)
            fallback.setDevicePixelRatio(dpr)
            return fallback

        reader = QImageReader(emoji_path)

        if reader.canRead():
            # Important for SVG: Define render size before reading
            reader.setScaledSize(QSize(target_size, target_size))

            image = reader.read()
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                pixmap.setDevicePixelRatio(dpr)

                # Apply margin
                if margin > 0:
                    final_size = int((size + (margin * 2)) * dpr)
                    final_pixmap = QPixmap(final_size, final_size)
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
    def getUrl(alias: str, margin: int, size: int, dpr: float, source_format: str) -> QUrl:
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
        query_params.addQueryItem("size", str(size))
        query_params.addQueryItem("dpr", str(dpr))
        query_params.addQueryItem("source_format", source_format)

        url.setQuery(query_params)

        return url
