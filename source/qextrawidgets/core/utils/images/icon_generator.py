"""
Pixmap and icon generation utilities for Qt applications.

This module exposes ``QIconGenerator``, a stateless utility class that converts
text characters (including emoji and color-font glyphs) and QtAwesome icon names
into high-quality ``QPixmap`` instances.  Every method is HiDPI-aware through an
explicit device-pixel-ratio (DPR) parameter and produces backing-store pixmaps at
physical resolution.

Key design decisions
--------------------
- ``QFontMetrics`` is intentionally avoided for glyph sizing.  Qt bug QTBUG-51024
  causes ``boundingRect()`` and ``horizontalAdvance()`` to return incorrect values
  on Windows when the display scale is 100% (DPR = 1.0) for color fonts such as
  Segoe UI Emoji or Apple Color Emoji.  The workaround is a one-time pixel scan
  using NumPy, cached indefinitely via ``lru_cache``.
- Supersampling (render at 4× then downscale) is used in :meth:`charToPixmap` to
  obtain smooth antialiasing equivalent to sub-pixel rendering without relying on
  platform-specific font hinting.
"""

from functools import lru_cache

import numpy as np
import qtawesome
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import (
    QPixmap,
    QPainter,
    QFont,
    QColor,
    QPainterPath,
)
from PySide6.QtWidgets import QStyle


class QIconGenerator:
    """Stateless factory for generating ``QPixmap`` objects from text and icons.

    All methods are exposed as ``@staticmethod`` or ``@classmethod`` — no
    instantiation is required or intended.  The class groups three distinct
    capabilities:

    * **Glyph rendering** (:meth:`charToPixmap`) — renders any Unicode character,
      including emoji and color-font glyphs, into a correctly sized, HiDPI-aware
      transparent pixmap.
    * **Image cropping** (:meth:`getCircularPixmap`) — crops an arbitrary pixmap
      into a circle with a center-aligned crop strategy.
    * **Composite icons** (:meth:`createIconWithBackground`) — composes a
      QtAwesome vector icon over a solid circular background at any DPR.

    HiDPI / DPR convention
    -----------------------
    All methods that accept a ``dpr`` parameter follow the same contract:

    1. The backing-store pixmap is created at ``logical_size × dpr`` physical pixels.
    2. ``QPainter`` operates in *physical* pixel coordinates (no DPR set on the
       pixmap while painting).
    3. ``setDevicePixelRatio(dpr)`` is called *after* ``painter.end()`` so that Qt
       displays the pixmap at the correct logical size on high-density screens.

    Note:
        :meth:`createIconWithBackground` is the exception — it sets DPR *before*
        painting intentionally, because it draws in logical coordinates and relies
        on Qt's automatic coordinate mapping.
    """

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    @lru_cache(maxsize=512)
    def _getGlyphCropRatio(char: str, font_family: str) -> tuple[float, float, float, float]:
        """Return the normalised ink bounding box of a glyph as crop ratios.

        This is the only reliable way to measure the *actual drawn area* of a
        character on Windows with DPR = 1.0.  ``QFontMetrics`` APIs
        (``boundingRect``, ``tightBoundingRect``, ``horizontalAdvance``) are
        intentionally avoided here because of Qt bug **QTBUG-51024**: on Windows
        at 100% display scale, those methods return values of 0 or 1 for color
        fonts (Segoe UI Emoji, Noto Color Emoji, etc.), making any ratio
        calculation collapse to the base size.

        Strategy
        --------
        1. Render the character at a fixed ``BASE_SIZE`` (128 px) onto a canvas
           that is 4× larger (512 × 512 px), centred via ``AlignCenter``.  The
           oversized canvas ensures no glyph is clipped regardless of descenders,
           side-bearings, or color-font bounding boxes that exceed the em-square.
        2. Convert the pixmap to a raw ARGB byte buffer and pass it to NumPy.
        3. Locate the first and last row/column whose alpha channel contains at
           least one non-zero pixel (vectorised — O(n) in C, not Python).
        4. Normalise all coordinates by ``CANVAS_SIZE`` so the returned ratios are
           independent of any specific resolution or DPR value.

        The result is cached indefinitely by ``lru_cache`` keyed on
        ``(char, font_family)``.  Subsequent calls for the same combination are
        O(1) dictionary lookups, so the expensive pixel scan runs at most once
        per glyph per session.

        Args:
            char:        Unicode character to measure (including multi-code-point
                         emoji sequences).
            font_family: Font family name (plain string, not a ``QFont`` object —
                         ``lru_cache`` requires hashable arguments).

        Returns:
            A 4-tuple ``(x_ratio, y_ratio, w_ratio, h_ratio)`` where each value
            is in the range ``[0.0, 1.0]`` and represents a fraction of
            ``CANVAS_SIZE``:

            - ``x_ratio`` — left edge of the ink bounding box.
            - ``y_ratio`` — top edge of the ink bounding box.
            - ``w_ratio`` — width of the ink bounding box.
            - ``h_ratio`` — height of the ink bounding box.

            Returns ``(0.0, 0.0, 1.0, 1.0)`` (full canvas) if no ink pixels are
            found, which is a safe fallback that prevents division-by-zero
            downstream.
        """
        BASE_SIZE   = 128
        CANVAS_SIZE = BASE_SIZE * 4  # 512 × 512 — generous margin on all sides

        font = QFont(font_family)
        font.setPixelSize(BASE_SIZE)

        # Render onto an oversized canvas to avoid any clipping
        pixmap = QPixmap(CANVAS_SIZE, CANVAS_SIZE)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setFont(font)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(
            QRect(0, 0, CANVAS_SIZE, CANVAS_SIZE),
            Qt.AlignmentFlag.AlignCenter,
            char,
        )
        painter.end()

        # Convert pixmap to a NumPy ARGB array — no Python-level pixel loop
        image = pixmap.toImage()
        ptr   = image.bits()
        arr   = np.frombuffer(ptr, dtype=np.uint8).reshape(CANVAS_SIZE, CANVAS_SIZE, 4)

        # Channel index 3 is alpha in Qt's default ARGB32 layout
        rows = np.any(arr[:, :, 3] > 0, axis=1)   # True for each row that has ink
        cols = np.any(arr[:, :, 3] > 0, axis=0)   # True for each col that has ink

        if not rows.any():
            # No ink found — return full-canvas fallback
            return 0.0, 0.0, 1.0, 1.0

        min_y, max_y = int(np.where(rows)[0][[0, -1]][0]), int(np.where(rows)[0][[0, -1]][1])
        min_x, max_x = int(np.where(cols)[0][[0, -1]][0]), int(np.where(cols)[0][[0, -1]][1])

        return (
            min_x / CANVAS_SIZE,
            min_y / CANVAS_SIZE,
            (max_x - min_x + 1) / CANVAS_SIZE,
            (max_y - min_y + 1) / CANVAS_SIZE,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    def charToPixmap(
        cls,
        char: str,
        target_size: QSize,
        font: QFont = QFont("Arial"),
        dpr: float = 1.0,
        color: QColor = QColor(Qt.GlobalColor.black),
    ) -> QPixmap:
        """Render a Unicode character into a transparent, HiDPI-aware ``QPixmap``.

        Supports all Unicode characters including color-font emoji (Segoe UI Emoji,
        Noto Color Emoji, Apple Color Emoji) on any platform and at any Windows
        display scale factor.

        Rendering pipeline
        ------------------
        1. **Measure** — call :meth:`_getGlyphCropRatio` to obtain the normalised
           ink bounding box of the glyph (result is cached after the first call).
        2. **Supersample** — compute a font pixel size that renders the glyph at
           ``SUPERSAMPLE × physical_size`` (4× by default).  Rendering at higher
           resolution and then downscaling produces noticeably sharper edges than
           rendering at the target size directly.
        3. **Draw** — paint the character onto an oversized canvas (``4 ×
           optimal_size``) centred with ``AlignCenter``.
        4. **Crop** — extract the exact ink region using the pre-computed ratios,
           eliminating all whitespace around the glyph.
        5. **Downscale** — reduce the cropped region to ``physical_size`` with
           ``SmoothTransformation``, which applies box-filter antialiasing.
        6. **Composite** — centre the scaled crop on the final physical canvas.
        7. **Tag DPR** — call ``setDevicePixelRatio(dpr)`` after all painting is
           complete so Qt maps the physical pixels to the correct logical size.

        Args:
            char:        The Unicode character to render (e.g. ``"A"``, ``"😀"``).
            target_size: Logical output size in pixels (the pixmap is square only
                         if ``target_size.width() == target_size.height()``).
            font:        Base font used for rendering.  The pixel size is ignored
                         and recalculated internally based on ``target_size`` and
                         ``dpr``.  For emoji, pass the system color emoji font.
                         Defaults to ``QFont("Arial")``.
            dpr:         Device pixel ratio of the target screen (e.g. ``2.0`` for
                         Retina / 4K displays).  Defaults to ``1.0``.
            color:       Foreground color applied via ``QPainter.setPen()``.  Only
                         affects non-color glyphs; color fonts render their own
                         colors regardless of this value.  Defaults to black.

        Returns:
            A transparent ``QPixmap`` at physical resolution
            ``(target_size.width() * dpr) × (target_size.height() * dpr)`` with
            ``devicePixelRatio`` set to ``dpr``.  The glyph is centred and scaled
            to fill the available space while preserving its aspect ratio.
            Returns an empty ``QPixmap`` if ``target_size.isEmpty()``.

        Example::

            pixmap = QIconGenerator.charToPixmap(
                "😀", QSize(48, 48), dpr=screen.devicePixelRatio()
            )
            label.setPixmap(pixmap)
        """
        if target_size.isEmpty():
            return QPixmap()

        physical_w = int(target_size.width()  * dpr)
        physical_h = int(target_size.height() * dpr)

        x_ratio, y_ratio, w_ratio, h_ratio = cls._getGlyphCropRatio(char, font.family())

        # Supersample factor: render at 4× physical size, then downscale.
        # Downscaling from 4× is equivalent to 4× SSAA and produces much
        # smoother edges than rendering at the exact target size.
        SUPERSAMPLE   = 4
        BASE_FRACTION = 1.0 / 4.0  # BASE_SIZE / CANVAS_SIZE ratio used in _getGlyphCropRatio

        render_w = physical_w * SUPERSAMPLE
        render_h = physical_h * SUPERSAMPLE

        # Derive the font pixel size that makes the glyph's ink area fill
        # the supersampled canvas exactly (limited by the tighter dimension).
        optimal_size = max(1, int(
            min(render_w / w_ratio, render_h / h_ratio) * BASE_FRACTION
        ))

        # Canvas is 4× the font size — matches the ratio used during measurement
        # in _getGlyphCropRatio, so the crop coordinates map correctly.
        CANVAS_SIZE = optimal_size * 4

        render_font = QFont(font)
        render_font.setPixelSize(optimal_size)

        canvas = QPixmap(CANVAS_SIZE, CANVAS_SIZE)
        canvas.fill(Qt.GlobalColor.transparent)

        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setFont(render_font)
        painter.setPen(color)
        painter.drawText(
            QRect(0, 0, CANVAS_SIZE, CANVAS_SIZE),
            Qt.AlignmentFlag.AlignCenter,
            char,
        )
        painter.end()

        # Crop the exact ink bounding box using the cached normalised ratios.
        # max(1, ...) prevents a zero-size QRect if the ratio rounds down to 0.
        ink_x = int(x_ratio * CANVAS_SIZE)
        ink_y = int(y_ratio * CANVAS_SIZE)
        ink_w = max(1, int(w_ratio * CANVAS_SIZE))
        ink_h = max(1, int(h_ratio * CANVAS_SIZE))
        ink_pixmap = canvas.copy(QRect(ink_x, ink_y, ink_w, ink_h))

        # Downscale the supersampled crop to the target physical size.
        # KeepAspectRatio ensures the glyph is never distorted.
        # SmoothTransformation applies a box filter equivalent to SSAA.
        scaled = ink_pixmap.scaled(
            QSize(physical_w, physical_h),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Centre the scaled glyph on the final physical canvas
        final = QPixmap(physical_w, physical_h)
        final.fill(Qt.GlobalColor.transparent)

        offset_x = (physical_w - scaled.width())  // 2
        offset_y = (physical_h - scaled.height()) // 2

        painter = QPainter(final)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawPixmap(offset_x, offset_y, scaled)
        painter.end()

        # Tag DPR after all painting — tells Qt to display these physical pixels
        # at the correct logical size without any additional scaling.
        final.setDevicePixelRatio(dpr)
        return final

    @staticmethod
    def getCircularPixmap(pixmap: QPixmap, size: int, dpr: float = 1.0) -> QPixmap:
        """Crop a pixmap into a circle using a centre-aligned square crop.

        The source pixmap is first cropped to the largest centred square that fits
        within it (preserving the subject at the centre), then the result is clipped
        to an ellipse and composited onto a transparent background.

        Uses ``QStyle.alignedRect`` for the square crop calculation and
        ``QPainterPath.addEllipse`` for the clip mask, both operating in logical
        coordinates so the output is correct at any DPR.

        Args:
            pixmap: Source pixmap to crop.  Returned unchanged if null.
            size:   Logical output size in pixels (the result is always square).
            dpr:    Device pixel ratio of the target screen.  The output pixmap
                    is created at ``size × dpr`` physical pixels.  Defaults to
                    ``1.0``.

        Returns:
            A ``size × size`` logical (``size*dpr × size*dpr`` physical) circular
            ``QPixmap`` with a transparent background, tagged with ``dpr``.
            Returns the original pixmap unchanged if it is null.

        Example::

            avatar = QIconGenerator.getCircularPixmap(profile_photo, 48, dpr=2.0)
            label.setPixmap(avatar)
        """
        if pixmap.isNull():
            return pixmap

        # Physical canvas size for HiDPI output
        physical_size = int(size * dpr)

        output = QPixmap(physical_size, physical_size)
        output.fill(Qt.GlobalColor.transparent)
        output.setDevicePixelRatio(dpr)

        painter = QPainter(output)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        # Clip to a circle in logical coordinates.
        # Because DPR is already set on the output pixmap, QPainter maps
        # logical (0, 0, size, size) to the correct physical pixels automatically.
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)

        # Centre-aligned square crop: take the largest square centred in the
        # source pixmap to avoid distorting non-square inputs (e.g. portrait photos).
        min_side  = min(pixmap.width(), pixmap.height())
        crop_size = QSize(min_side, min_side)

        source_rect = QStyle.alignedRect(
            Qt.LayoutDirection.LeftToRight,
            Qt.AlignmentFlag.AlignCenter,
            crop_size,    # desired crop dimensions
            pixmap.rect(),  # total source rectangle
        )

        # Map source_rect (pixels in the original pixmap) into the logical
        # target rect (0, 0, size, size) — Qt handles the scaling.
        target_rect = QRect(0, 0, size, size)
        painter.drawPixmap(target_rect, pixmap, source_rect)

        painter.end()
        return output

    @staticmethod
    def createIconWithBackground(
        icon_name: str,
        background_color: str,
        size: int = 48,
        dpr: float = 1.0,
        icon_color: str = "white",
        scale_factor: float = 0.6,
    ) -> QPixmap:
        """Compose a QtAwesome icon over a solid circular background.

        Generates a circular filled disc using ``background_color``, then centres
        a QtAwesome vector icon on top of it.  Both the disc and the icon are
        rendered at physical resolution (``size × dpr``) for HiDPI displays.

        DPR note
        --------
        Unlike :meth:`charToPixmap`, this method sets ``devicePixelRatio`` on the
        output pixmap *before* painting.  This causes ``QPainter`` to operate in
        logical coordinates (``0..size``) while the backing store is
        ``size*dpr × size*dpr`` physical pixels.  The same DPR is then applied to
        the inner icon pixmap so that ``QStyle.alignedRect`` (which works in
        logical space) centres it correctly.

        Args:
            icon_name:        QtAwesome icon identifier (e.g. ``"fa5s.user"``,
                              ``"mdi.home"``).  See the QtAwesome documentation for
                              all available icon sets.
            background_color: Background fill color in any format accepted by
                              ``QColor`` (e.g. ``"#FF5733"``, ``"red"``,
                              ``"rgba(255, 87, 51, 200)"``).
            size:             Logical size of the output pixmap in pixels.  The
                              actual backing store is ``size × dpr`` pixels.
                              Defaults to ``48``.
            dpr:              Device pixel ratio of the target screen.
                              Defaults to ``1.0``.
            icon_color:       Foreground color of the QtAwesome icon, passed
                              directly to ``qtawesome.icon()``.  Defaults to
                              ``"white"``.
            scale_factor:     Fraction of ``size`` used for the inner icon
                              (``0.0`` – ``1.0``).  A value of ``0.6`` means the
                              icon occupies 60% of the circle diameter.
                              Defaults to ``0.6``.

        Returns:
            A ``QPixmap`` at physical resolution ``(size*dpr) × (size*dpr)`` with
            ``devicePixelRatio`` set to ``dpr``, showing the icon centred on a
            filled circle.

        Example::

            badge = QIconGenerator.createIconWithBackground(
                "fa5s.bell", "#5865F2", size=40, dpr=screen.devicePixelRatio()
            )
            button.setIcon(QIcon(badge))
        """
        physical_width  = int(size * dpr)
        physical_height = int(size * dpr)

        final_pixmap = QPixmap(physical_width, physical_height)
        final_pixmap.fill(Qt.GlobalColor.transparent)

        # Set DPR before painting so QPainter uses logical coordinates (0..size).
        # This is intentionally different from charToPixmap, which sets DPR after
        # painting because it works exclusively in physical pixel space.
        final_pixmap.setDevicePixelRatio(dpr)

        painter = QPainter(final_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Draw the circular background in logical coordinates
        painter.setBrush(QColor(background_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size, size)

        # Request the icon pixmap at physical resolution from QtAwesome.
        # qtawesome.icon() returns a QIcon backed by a scalable font glyph,
        # so requesting physical_icon_size pixels gives maximum sharpness.
        logical_icon_size  = int(size * scale_factor)
        physical_icon_size = int(logical_icon_size * dpr)

        icon = qtawesome.icon(icon_name, color=icon_color)
        icon_pixmap = icon.pixmap(physical_icon_size, physical_icon_size)

        # Tag the icon pixmap with DPR so alignedRect (logical space) and
        # drawPixmap produce correct results when composited onto final_pixmap.
        icon_pixmap.setDevicePixelRatio(dpr)

        # Centre the icon within the logical bounding rect of the circle
        centered_rect = QStyle.alignedRect(
            Qt.LayoutDirection.LeftToRight,
            Qt.AlignmentFlag.AlignCenter,
            QSize(logical_icon_size, logical_icon_size),
            QRect(0, 0, size, size),
        )

        painter.drawPixmap(centered_rect, icon_pixmap)
        painter.end()

        return final_pixmap