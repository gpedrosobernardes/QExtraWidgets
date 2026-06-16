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
import qtawesome
from PySide6.QtCore import Qt, QSize, QRect, QPointF
from PySide6.QtGui import (
    QPixmap,
    QPainter,
    QColor,
    QPainterPath,
)
from PySide6.QtWidgets import QStyle


class QIconGenerator:
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