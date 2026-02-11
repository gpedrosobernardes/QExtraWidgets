import qtawesome
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import (
    QPixmap,
    QPainter,
    QFont,
    QColor,
    QFontMetrics,
    QPainterPath,
)
from PySide6.QtWidgets import QStyle


class QIconGenerator:
    """Class responsible for generating Pixmaps and icons based on text/fonts."""

    @staticmethod
    def calculateMaxPixelSize(text: str, font: QFont, target_size: QSize) -> int:
        """
        Calculates the maximum pixel size the font can have so the text fits within target_size.

        Args:
            text (str): Text to be measured.
            font (QFont): The font configuration (family, weight, italic).
            target_size (QSize): The available space.

        Returns:
            int: The calculated pixel size.
        """
        if not text:
            return 12  # safe fallback size

        # 1. Work with a copy to avoid altering the original font externally
        temp_font = QFont(font)

        # 2. Use an arbitrary large base size for calculation precision
        base_pixel_size = 100
        temp_font.setPixelSize(base_pixel_size)

        fm = QFontMetrics(temp_font)

        # 3. Get dimensions occupied by text at base size
        # horizontalAdvance: Total width including natural spacing
        base_width = fm.horizontalAdvance(text)
        # height: Total line height (Ascent + Descent).
        base_height = fm.height()

        if base_width == 0 or base_height == 0:
            return base_pixel_size

        # 4. Calculate scale ratio for each dimension
        width_ratio = target_size.width() / base_width
        height_ratio = target_size.height() / base_height

        # 5. The Limiting Factor is the SMALLEST ratio (to ensure it fits both width and height)
        final_scale_factor = min(width_ratio, height_ratio)

        # 6. Apply factor to base size
        new_pixel_size = int(base_pixel_size * final_scale_factor)

        # Returns at least 1 to avoid rendering errors
        return max(1, new_pixel_size)

    @classmethod
    def charToPixmap(
        cls,
        char: str,
        target_size: QSize,
        font: QFont = QFont("Arial"),
        color: QColor = QColor(Qt.GlobalColor.black),
    ) -> QPixmap:
        """
        Generates a QPixmap of a specific size containing a character rendered at the largest possible size.

        Args:
            char (str): The character to be rendered.
            target_size (QSize): The final image size (e.g., 64x64).
            font (QFont): The base font (will be resized internally).
            color (QColor): The text color.

        Returns:
            QPixmap: Transparent image with the character centered.
        """
        if target_size.isEmpty():
            return QPixmap()

        # 1. Calculate optimal font size to fill target_size
        optimal_size = cls.calculateMaxPixelSize(char, font, target_size)

        # 2. Configure font with calculated size
        render_font = QFont(font)
        render_font.setPixelSize(optimal_size)

        # 3. Create Pixmap with exact requested size
        pixmap = QPixmap(target_size)
        pixmap.fill(Qt.GlobalColor.transparent)

        # 4. Configure Painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setFont(render_font)
        painter.setPen(color)

        # 5. Draw text centered in Pixmap rectangle
        # Qt.AlignCenter handles X and Y positioning automatically
        rect = pixmap.rect()
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, char)

        painter.end()

        return pixmap

    @staticmethod
    def getCircularPixmap(pixmap: QPixmap, size: int, dpr: float = 1.0) -> QPixmap:
        """Creates a circular pixmap (center crop) with HiDPI support.

        Uses QStyle to calculate alignment for proper center cropping.

        Args:
            pixmap: Source pixmap to crop.
            size: Logical size of the output circular pixmap.
            dpr: Device Pixel Ratio for HiDPI displays (e.g., 1.0, 1.25, 2.0).

        Returns:
            QPixmap: Circular pixmap with transparent background.
        """
        if pixmap.isNull():
            return pixmap

        # 1. Configure physical size for high density (Retina/4K)
        physical_size = int(size * dpr)

        output = QPixmap(physical_size, physical_size)
        output.fill(Qt.GlobalColor.transparent)
        output.setDevicePixelRatio(dpr)

        # 2. Configure Painter
        painter = QPainter(output)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        # 3. Apply circular clip path (using logical coordinates)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)

        # 4. Calculate center crop using QStyle.alignedRect
        # Find the smallest side to create a square crop
        min_side = min(pixmap.width(), pixmap.height())
        crop_size = QSize(min_side, min_side)

        # QStyle automatically calculates centered rectangle within original image
        source_rect = QStyle.alignedRect(
            Qt.LayoutDirection.LeftToRight,
            Qt.AlignmentFlag.AlignCenter,
            crop_size,  # Square size we want to crop
            pixmap.rect(),  # Total rectangle of original image
        )

        # 5. Draw
        # source_rect (center of original) is drawn into target_rect (final circle)
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
        """Creates a high-quality (HiDPI) icon with circular background.

        Args:
            icon_name: QtAwesome icon name (e.g., 'fa5s.user').
            background_color: Background color in any Qt-supported format (e.g., '#FF5733', 'red').
            size: Logical desired size (e.g., 48).
            dpr: Device Pixel Ratio of the window (e.g., 1.0, 1.25, 2.0).
            icon_color: Icon foreground color.
            scale_factor: Icon size relative to background (0.0 to 1.0).

        Returns:
            QPixmap: High-quality pixmap with icon on circular background.
        """
        # 1. Calculate PHYSICAL size (actual pixels)
        # If size=48 and dpr=2 (4K/Retina display), create a 96x96 pixel image
        physical_width = int(size * dpr)
        physical_height = int(size * dpr)

        # 2. Create Pixmap with physical size
        final_pixmap = QPixmap(physical_width, physical_height)
        final_pixmap.fill(Qt.GlobalColor.transparent)

        # IMPORTANT: Tell the pixmap about its pixel density
        # This makes QPainter 'think' in logical coordinates (48x48)
        # while drawing in high resolution (96x96)
        final_pixmap.setDevicePixelRatio(dpr)

        # 3. Start painting
        painter = QPainter(final_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # 4. Draw background (using logical coordinates 0..size)
        painter.setBrush(QColor(background_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size, size)

        # 5. Generate internal icon (QtAwesome)
        # Request high-resolution icon from qtawesome to ensure quality
        logical_icon_size = int(size * scale_factor)
        physical_icon_size = int(logical_icon_size * dpr)

        icon = qtawesome.icon(icon_name, color=icon_color)
        # Generate raw pixmap in high resolution
        icon_pixmap_high_resolution = icon.pixmap(
            physical_icon_size, physical_icon_size
        )

        # Set DPR on internal icon for proper alignment
        icon_pixmap_high_resolution.setDevicePixelRatio(dpr)

        # 6. Center with QStyle.alignedRect (using logical coordinates)
        centered_rect = QStyle.alignedRect(
            Qt.LayoutDirection.LeftToRight,
            Qt.AlignmentFlag.AlignCenter,
            QSize(logical_icon_size, logical_icon_size),  # Logical size
            QRect(0, 0, size, size),  # Logical area
        )

        # 7. Draw
        painter.drawPixmap(centered_rect, icon_pixmap_high_resolution)
        painter.end()

        return final_pixmap
