from qextrawidgets.core.utils.emojis import QEmojiPixmapCache


class QGlobalEmojiPixmapCache:
    caches = {}

    @classmethod
    def ensureCache(cls, font_family: str) -> QEmojiPixmapCache:
        if font_family not in cls.caches:
            cls.caches[font_family] = QEmojiPixmapCache(font_family)

        return cls.caches[font_family]