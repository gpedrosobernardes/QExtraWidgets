"""
Emoji image loading, processing, and caching utilities for Qt applications.

This module exposes ``QEmojiImageProvider``, a ``QObject``-based provider that
resolves emoji characters to ``QPixmap`` instances.  It supports three rendering
back-ends (PNG files, SVG files, and arbitrary Qt fonts), is HiDPI-aware through
an explicit device-pixel-ratio parameter, and uses ``QPixmapCache`` to avoid
redundant disk I/O across repeated requests.

Typical usage::

    provider = QEmojiImageProvider(size=32, dpr=2.0, source="png")
    pixmap = provider.getPixmap("😀")          # logical 32 px, physical 64 px
"""

from PySide6.QtCore import QSize, QUrl, QUrlQuery, QObject, Signal
from PySide6.QtGui import QPixmap, QPixmapCache, Qt, QImageReader, QFont
from emoji_data_python import char_to_unified
from twemoji_api import get_emoji_path

from qextrawidgets.core.utils.emojis.emoji_utils import QEmojiUtils
from qextrawidgets.core.utils.images import QIconGenerator
from qextrawidgets.gui.items import QIconItem


class QEmojiImageProvider(QObject):
    """Loads, scales, and caches emoji images for use in Qt widgets.

    ``QEmojiImageProvider`` centralizes all emoji-to-pixmap resolution logic.
    It keeps track of three rendering parameters — logical size, device-pixel
    ratio, and rendering source — and exposes both instance-level convenience
    methods (which use those stored parameters) and static counterparts (which
    accept every parameter explicitly, useful when no persistent provider object
    is needed).

    Rendering sources
    -----------------
    ``source`` can be one of three values:

    * ``"png"``  — loads a raster PNG file from the Twemoji asset library.
    * ``"svg"``  — loads a vector SVG file from the Twemoji asset library.
    * ``<font>`` — any other string is interpreted as a Qt font family name and
      the emoji is rendered as text via :class:`QIconGenerator`.

    HiDPI / DPR handling
    --------------------
    All pixmaps are created at *physical* resolution (``size × dpr``) and then
    tagged with ``setDevicePixelRatio(dpr)`` so that Qt displays them at the
    correct *logical* size on high-density screens.

    Caching
    -------
    Every resolved pixmap is stored in ``QPixmapCache`` under a URL key that
    encodes the emoji alias, logical size, DPR, and source (see
    :meth:`getUrlBy`).  Subsequent requests for the same combination are served
    directly from the cache without touching the filesystem.

    Signals:
        sourceChanged (str): Emitted when :meth:`setSource` changes the active
            rendering source.  The new source string is passed as the argument.

    Example::

        provider = QEmojiImageProvider(size=48, dpr=screen.devicePixelRatio())
        pixmap = provider.getPixmap("👍")
        label.setPixmap(pixmap)
    """

    sourceChanged = Signal(str)
    sizeChanged = Signal(int)
    devicePixelRatioChanged = Signal(float)

    def __init__(self, size: int, dpr: float, source: str = "png") -> None:
        """Initialise the provider with fixed rendering parameters.

        Args:
            size:   Logical pixel size of the emoji image (width = height).
            dpr:    Device pixel ratio of the target screen (e.g. ``2.0`` for
                    Retina displays).  Used to compute the physical resolution.
            source: Rendering back-end to use.  ``"png"`` or ``"svg"`` select
                    Twemoji file assets; any other value is treated as a font
                    family name.  Defaults to ``"png"``.
        """
        super().__init__()
        self._size = size
        self._dpr = dpr
        self._source = source

    # ------------------------------------------------------------------
    # Static helpers
    # ------------------------------------------------------------------

    @staticmethod
    def getFallbackBy(size: int, dpr: float) -> QPixmap:
        """Create a fully transparent placeholder pixmap.

        Used whenever an emoji asset cannot be located or read, ensuring
        callers always receive a valid (though invisible) ``QPixmap`` rather
        than a null one.

        Args:
            size: Physical pixel size (width and height) of the placeholder.
            dpr:  Device pixel ratio to tag the pixmap with.

        Returns:
            A ``size × size`` transparent ``QPixmap`` with its device-pixel
            ratio set to ``dpr``.
        """
        fallback = QPixmap(size, size)
        fallback.fill(Qt.GlobalColor.transparent)
        fallback.setDevicePixelRatio(dpr)
        return fallback

    @staticmethod
    def getPixmapBy(
        emoji: str,
        size: int,
        dpr: float = 1.0,
        source: str = "png",
    ) -> QPixmap:
        """Resolve an emoji character to a scaled, cache-backed ``QPixmap``.

        Resolution order:

        1. Check ``QPixmapCache`` for a previously resolved pixmap.
        2. On a cache miss, load from the appropriate back-end (PNG, SVG, or
           font rendering).
        3. Store the result in ``QPixmapCache`` for future requests.
        4. Return a transparent fallback pixmap if loading fails at any step.

        Args:
            emoji:  Unicode emoji character to render (e.g. ``"😀"``).
            size:   Logical size in pixels (the pixmap is square).
            dpr:    Device pixel ratio.  The pixmap is created at
                    ``size × dpr`` physical pixels and tagged accordingly.
                    Defaults to ``1.0``.
            source: Rendering back-end: ``"png"``, ``"svg"``, or a font family
                    name.  Defaults to ``"png"``.

        Returns:
            A ``QPixmap`` at physical resolution ``(size * dpr) × (size * dpr)``
            with ``devicePixelRatio`` set to ``dpr``.  Returns a transparent
            fallback pixmap if the asset cannot be loaded.
        """
        # 1. Physical (backing-store) size in pixels
        target_size = int(size * dpr)

        # 2. Build a deterministic cache key from all rendering parameters
        cache_url = QEmojiImageProvider.getUrlBy(char_to_unified(emoji), size, dpr, source)

        # 3. Fast path: return cached pixmap if available
        pixmap = QPixmap()
        if QPixmapCache.find(cache_url.toString(), pixmap):
            return pixmap

        # --- Cache miss: load from the selected back-end ---

        if source in ("png", "svg"):
            emoji_path = str(get_emoji_path(emoji, source))
            if not emoji_path:
                return QEmojiImageProvider.getFallbackBy(target_size, dpr)

            # QImageReader is more memory-efficient than constructing QPixmap(path)
            # directly, and is mandatory for SVG because it allows pre-scaling
            # before decoding.
            reader = QImageReader(emoji_path)

            if reader.canRead():
                # For SVG: set the target size *before* read() so the renderer
                # produces pixels at the correct resolution instead of decoding
                # at the document's intrinsic size and then rescaling.
                reader.setScaledSize(QSize(target_size, target_size))

                image = reader.read()
                if not image.isNull():
                    pixmap = QPixmap.fromImage(image)
                    pixmap.setDevicePixelRatio(dpr)
                    QPixmapCache.insert(cache_url.toString(), pixmap)
                    return pixmap

        else:
            # Font back-end: render the emoji glyph via QIconGenerator
            pixmap = QIconGenerator.charToPixmap(
                emoji, QSize(size, size), QFont(source), dpr
            )
            QPixmapCache.insert(cache_url.toString(), pixmap)
            return pixmap

        # All loading attempts failed — return transparent placeholder
        return QEmojiImageProvider.getFallbackBy(target_size, dpr)

    @staticmethod
    def getUrlBy(alias: str, size: int, dpr: float, source: str) -> QUrl:
        """Build a unique ``QUrl`` cache key for a specific emoji + render config.

        The URL encodes every parameter that affects the visual output of a
        pixmap, ensuring distinct keys for the same emoji rendered at different
        sizes, DPRs, or sources.

        URL format::

            emoji://<alias>?size=<size>&dpr=<dpr>&source=<source>

        Example::

            emoji://1F600?size=32&dpr=2.0&source=png

        Args:
            alias:  Unified emoji code point string (e.g. ``"1F600"``),
                    typically obtained via ``char_to_unified()``.
            size:   Logical size used for the ``size`` query parameter.
            dpr:    Device pixel ratio used for the ``dpr`` query parameter.
            source: Rendering source used for the ``source`` query
                    parameter.

        Returns:
            A ``QUrl`` instance suitable for use as a ``QPixmapCache`` key.
        """
        url = QUrl()
        url.setScheme("emoji")
        url.setPath(alias)

        query_params = QUrlQuery()
        query_params.addQueryItem("size", str(size))
        query_params.addQueryItem("dpr", str(dpr))
        query_params.addQueryItem("source", source)

        url.setQuery(query_params)
        return url

    @staticmethod
    def getPixmapFromIconItemBy(
        icon_item: QIconItem,
        size: int,
        dpr: float,
        source: str,
    ) -> QPixmap:
        """Resolve a ``QIconItem``'s emoji — including its skin tone — to a pixmap.

        Reads the base emoji character and the Fitzpatrick skin tone modifier
        from ``icon_item``, combines them via :func:`QEmojiUtils.combineEmojiWithSkinTone`,
        and delegates to :meth:`getPixmapBy` for the actual loading.

        Args:
            icon_item: Item whose ``EditRole`` data holds the base emoji
                       character and whose ``ColorModifierRole`` data holds
                       the skin tone code (or an empty string for the default
                       tone).
            size:      Logical pixel size.
            dpr:       Device pixel ratio.
            source:    Rendering back-end (``"png"``, ``"svg"``, or font name).

        Returns:
            The resolved ``QPixmap``, or a transparent fallback pixmap if
            the emoji character cannot be determined.
        """
        emoji_char = QEmojiUtils.getEmojiWithSkinToneByIconItem(icon_item)

        if emoji_char is None:
            return QEmojiImageProvider.getFallbackBy(size, dpr)

        return QEmojiImageProvider.getPixmapBy(emoji_char.char, size, dpr, source)

    # ------------------------------------------------------------------
    # Instance-level convenience wrappers
    # ------------------------------------------------------------------

    def getUrl(self, alias: str) -> QUrl:
        """Build a cache key URL using this provider's stored parameters.

        Convenience wrapper around :meth:`getUrlBy` that substitutes the
        instance's ``size``, ``dpr``, and ``source`` automatically.

        Args:
            alias: Unified emoji code point string (e.g. ``"1F600"``).

        Returns:
            A ``QUrl`` cache key for the given alias under current settings.
        """
        return self.getUrlBy(alias, self._size, self._dpr, self.getSource())

    def getPixmap(self, emoji: str) -> QPixmap:
        """Load an emoji pixmap using this provider's stored parameters.

        Convenience wrapper around :meth:`getPixmapBy` that substitutes the
        instance's ``size``, ``dpr``, and ``source`` automatically.

        Args:
            emoji: Unicode emoji character (e.g. ``"😀"``).

        Returns:
            The resolved ``QPixmap``, or a transparent fallback on failure.
        """
        return self.getPixmapBy(emoji, self._size, self._dpr, self.getSource())

    def getPixmapFromIconItem(self, icon_item: QIconItem) -> QPixmap:
        """Resolve a ``QIconItem``'s emoji to a pixmap using stored parameters.

        Convenience wrapper around :meth:`getPixmapFromIconItemBy` that
        substitutes the instance's ``size``, ``dpr``, and ``source``
        automatically.

        Args:
            icon_item: Item carrying the base emoji and skin tone modifier.

        Returns:
            The resolved ``QPixmap``, or a transparent fallback on failure.
        """
        return self.getPixmapFromIconItemBy(
            icon_item, self._size, self._dpr, self.getSource()
        )

    # ------------------------------------------------------------------
    # Source property
    # ------------------------------------------------------------------

    def getSource(self) -> str:
        """Return the active rendering source.

        Returns:
            ``"png"``, ``"svg"``, or a font family name, depending on which
            back-end this provider is currently configured to use.
        """
        return self._source

    def setSource(self, source: str) -> None:
        """Change the rendering source and notify listeners.

        If ``source`` differs from the current value, updates the internal
        state and emits :attr:`sourceChanged` with the new source string.
        No-op if the value is unchanged (avoids spurious signal emissions).

        Args:
            source: New rendering back-end: ``"png"``, ``"svg"``, or a font
                    family name.
        """
        if source != self._source:
            self._source = source
            self.sourceChanged.emit(self._source)

    def getSize(self) -> int:
        """Return the current logical emoji size in pixels.

        Returns:
            The logical pixel size (width = height) used when resolving
            pixmaps via the instance-level convenience methods.  The
            physical backing-store size is ``getSize() × dpr``.
        """
        return self._size

    def setSize(self, size: int) -> None:
        """Change the logical emoji size and notify listeners.

        If ``size`` differs from the current value, updates the internal
        state and emits :attr:`sizeChanged` with the new value.
        No-op if the value is unchanged (avoids spurious signal emissions).

        Note:
            Changing the size does **not** invalidate ``QPixmapCache`` entries
            from the previous size.  Previously cached pixmaps remain in the
            cache and will be served if a caller requests the old size again.

        Args:
            size: New logical pixel size (width = height).  Must be > 0.
        """
        if size != self._size:
            self._size = size
            self.sizeChanged.emit(self._size)

    def getDevicePixelRatio(self) -> float:
        """Return the current device pixel ratio.

        Returns:
            The DPR used when resolving pixmaps via the instance-level
            convenience methods.  The physical backing-store size of any
            produced pixmap is ``getSize() × getDevicePixelRatio()``.
        """
        return self._dpr

    def setDevicePixelRatio(self, dpr: float) -> None:
        """Change the device pixel ratio and notify listeners.

        If ``dpr`` differs from the current value, updates the internal
        state and emits :attr:`devicePixelRatioChanged` with the new value.
        No-op if the value is unchanged (avoids spurious signal emissions).

        Note:
            Changing the DPR does **not** invalidate ``QPixmapCache`` entries
            produced with the previous DPR.  Those pixmaps remain cached and
            will be served if a caller explicitly requests the old DPR again.
            If stale entries are a concern, call ``QPixmapCache.clear()``
            before or after updating the DPR.

        Args:
            dpr: New device pixel ratio. Typical values are ``1.0`` (standard
                 displays), ``1.25`` / ``1.5`` (Windows intermediate scales),
                 and ``2.0`` (Retina / 4K displays). Must be > 0.
        """
        if dpr != self._dpr:
            self._dpr = dpr
            self.devicePixelRatioChanged.emit(self._dpr)