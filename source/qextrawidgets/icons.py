import typing

import qtawesome
from PySide6.QtCore import QRect, Qt, QSize, QPoint
from PySide6.QtGui import QIcon, QIconEngine, QPainter, QPixmap, QPalette, QColor
from PySide6.QtWidgets import QApplication


class ThemeResponsiveIconEngine(QIconEngine):
    """
    Dynamic icon engine that acts as a Proxy for an original QIcon.
    Adjusts rendering based on the smallest available dimension to avoid clipping.
    """

    def __init__(self, icon: QIcon):
        super().__init__()
        self._source_icon = icon

        # Simple Cache
        self._cached_pixmap: typing.Optional[QPixmap] = None
        self._cache_key: typing.Optional[tuple] = None  # (width, height, mode, state, color_rgba)

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State):
        """
        Paints the icon centered, limited by the smallest dimension of the rectangle.
        """
        # 1. Determine bounding box size
        min_side = min(rect.width(), rect.height())

        # Safety margin (2px each side) to avoid anti-aliasing clipping
        safe_side = min_side - 4

        if safe_side <= 0:
            return

        bounding_size = QSize(safe_side, safe_side)

        # 2. Get Colored Pixmap
        # We request the pixmap based on this bounding size
        pixmap = self._getColoredPixmap(bounding_size, mode, state)

        if pixmap.isNull():
            return

        # 3. Scale Calculation (Maintaining Aspect Ratio)
        pixmap_size = pixmap.size()

        # CORRECTION HERE: QSize.scaled accepts only (Size, Mode).
        # Visual smoothing is done by painter.setRenderHint later.
        scaled_size = pixmap_size.scaled(
            bounding_size,
            Qt.AspectRatioMode.KeepAspectRatio
        )

        # 4. Centering
        # Calculates position (x, y) to center in original rect
        x = rect.x() + (rect.width() - scaled_size.width()) // 2
        y = rect.y() + (rect.height() - scaled_size.height()) // 2

        target_rect = QRect(x, y, scaled_size.width(), scaled_size.height())

        # 5. Drawing
        # Activates smoothing when drawing pixels on screen
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.drawPixmap(target_rect, pixmap)

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        """Returns processed pixmap."""
        return self._getColoredPixmap(size, mode, state)

    def addPixmap(self, pixmap: QPixmap, mode: QIcon.Mode, state: QIcon.State):
        self._source_icon.addPixmap(pixmap, mode, state)
        self._clearCache()

    def addFile(self, fileName: str, size: QSize, mode: QIcon.Mode, state: QIcon.State):
        self._source_icon.addFile(fileName, size, mode, state)
        self._clearCache()

    def availableSizes(self, mode: QIcon.Mode = QIcon.Mode.Normal, state: QIcon.State = QIcon.State.Off) -> typing.List[QSize]:
        return self._source_icon.availableSizes(mode, state)

    def actualSize(self, size: QSize, mode: QIcon.Mode = QIcon.Mode.Normal, state: QIcon.State = QIcon.State.Off) -> QSize:
        return self._source_icon.actualSize(size, mode, state)

    def clone(self):
        return ThemeResponsiveIconEngine(self._source_icon)

    # --- Internal Logic ---

    def _getColoredPixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        # 1. Theme Color
        palette = QApplication.palette()
        if mode == QIcon.Mode.Disabled:
            target_color = palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText)
        else:
            target_color = palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText)

        # 2. Cache Check
        current_key = (size.width(), size.height(), mode, state, target_color.rgba())

        if self._cached_pixmap and self._cache_key == current_key:
            return self._cached_pixmap

        # 3. Get Original Pixmap
        base_pixmap = self._source_icon.pixmap(size, mode, state)

        if base_pixmap.isNull():
            return QPixmap()

        # 4. Colorize
        colored_pixmap = self._generateColoredPixmap(base_pixmap, target_color)

        # Update Cache
        self._cached_pixmap = colored_pixmap
        self._cache_key = current_key

        return colored_pixmap

    def _generateColoredPixmap(self, base: QPixmap, color: QColor) -> QPixmap:
        colored = QPixmap(base.size())
        colored.fill(Qt.GlobalColor.transparent)

        p = QPainter(colored)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Paint color
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        p.fillRect(colored.rect(), color)

        # Cut shape
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        p.drawPixmap(0, 0, base)
        p.end()

        return colored

    def _clearCache(self):
        self._cached_pixmap = None
        self._cache_key = None


class QThemeResponsiveIcon(QIcon):
    """
    QIcon wrapper that applies automatic coloring based on system theme.
    The icon adjusts to the smallest available space maintaining aspect ratio.
    """
    def __init__(self, source: typing.Union[str, QPixmap, QIcon], size: int = 64):
        icon = QIcon()

        if isinstance(source, QIcon):
            icon = source
        elif isinstance(source, str):
            icon = QIcon(source)
        elif isinstance(source, QPixmap):
            icon = QIcon()
            icon.addPixmap(source)

        super().__init__(ThemeResponsiveIconEngine(icon))

    @staticmethod
    def fromAwesome(icon_name: str, size: int = 64, **kwargs):
        return QThemeResponsiveIcon(qtawesome.icon(icon_name, **kwargs), size)
