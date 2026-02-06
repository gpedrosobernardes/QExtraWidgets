from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QFont, QColor, QFontMetrics


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
