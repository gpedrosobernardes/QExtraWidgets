from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QFontDatabase, QColorConstants
from PySide6.QtWidgets import QApplication


def is_dark_mode() -> bool:
    """Checks if the system application is in dark mode.

    Returns:
        bool: True if dark mode is active, False otherwise.
    """
    style_hints = QApplication.styleHints()
    color_scheme = style_hints.colorScheme()
    return color_scheme.value == 2


def get_max_pixel_size(text: str, font_name: str, target_size: QSize) -> int:
    """Calculates the maximum font pixel size to fit text within a target size.

    Maintains aspect ratio while ensuring the entire text is visible.

    Args:
        text (str): Text to measure.
        font_name (str): Font family name.
        target_size (QSize): Available space.

    Returns:
        int: Maximum pixel size.
    """
    if not text:
        return 12  # safe fallback size

    # 1. Use an arbitrary base size for initial measurement
    base_pixel_size = 100
    font = QFont(font_name)
    font.setPixelSize(base_pixel_size)

    fm = QFontMetrics(font)

    # 2. Get dimensions occupied by text at base size
    # horizontalAdvance: Total width including natural letter spacing
    base_width = fm.horizontalAdvance(text)
    # height: Total line height (Ascent + Descent).
    # Safer than boundingRect().height() to avoid clipping accents/descenders.
    base_height = fm.height()

    if base_width == 0 or base_height == 0:
        return base_pixel_size

    # 3. Calculate scale ratio for each dimension
    width_ratio = target_size.width() / base_width
    height_ratio = target_size.height() / base_height

    # 4. Limiting Factor: Choose the SMALLEST ratio.
    final_scale_factor = min(width_ratio, height_ratio)

    # 5. Apply factor to base size
    new_pixel_size = int(base_pixel_size * final_scale_factor)

    # Optional: Safety lock to not return 0
    return max(1, new_pixel_size)


from PySide6.QtGui import QPixmap, QPainter, QFont, QColor, QFontMetrics
from PySide6.QtCore import Qt, QSize


def char_to_pixmap(char: str, font: QFont, color: QColor = Qt.GlobalColor.black) -> QPixmap:
    """
    Renders a single character from a specific font into a QPixmap.

    Args:
        char (str): The character to render.
        font (QFont): The font configuration.
        color (QColor): The color of the text.

    Returns:
        QPixmap: A transparent image containing the rendered character.
    """
    # 1. Calculate the exact bounding box of the character
    metrics = QFontMetrics(font)
    rect = metrics.boundingRect(char)

    # 2. Create a Pixmap with the size of the character
    # We add a small padding to avoid anti-aliasing clipping
    width = rect.width()
    height = rect.height()

    if width == 0 or height == 0:
        return QPixmap()

    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)

    # 3. Paint the character
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    painter.setFont(font)
    painter.setPen(color)

    # 4. Draw text
    # The rect.left() and rect.top() might be negative (e.g. for 'j' or 'Á'),
    # so we subtract them to shift the drawing into the visible area (0,0).
    x_pos = -rect.left()
    y_pos = -rect.top()

    painter.drawText(x_pos, y_pos, char)
    painter.end()

    return pixmap


class QColorUtils:
    """Utility class for color-related operations."""

    @staticmethod
    def getContrastingTextColor(bg_color: QColor) -> QColor:
        """Returns Qt.black or Qt.white depending on the background color luminance.

        Formula based on human perception (NTSC conversion formula).

        Args:
            bg_color (QColor): Background color to calculate contrast against.

        Returns:
            QColor: Contrasting text color (Black or White).
        """
        r = bg_color.red()
        g = bg_color.green()
        b = bg_color.blue()

        # Calculate weighted brightness
        # 0.299R + 0.587G + 0.114B
        luminance = (0.299 * r) + (0.587 * g) + (0.114 * b)

        # Common threshold is 128 (half of 255).
        # If brighter than 128, background is light -> Black Text
        # If darker, background is dark -> White Text
        return QColorConstants.Black if luminance > 128 else QColorConstants.White


class QEmojiFonts:
    """Utility class for loading and accessing emoji fonts."""

    TwemojiFontFamily = None

    @classmethod
    def loadTwemojiFont(cls) -> str:
        """Loads the bundled Twemoji font into the application font database.

        Returns:
            str: The loaded font family name.
        """
        if not cls.TwemojiFontFamily:
            root_folder_path = Path(__file__).parent
            fonts_folder_path = root_folder_path / "fonts"
            file_path = fonts_folder_path / "Twemoji-17.0.2.ttf"

            id_ = QFontDatabase.addApplicationFont(str(file_path))
            family = QFontDatabase.applicationFontFamilies(id_)[0]

            cls.TwemojiFontFamily = family

        return cls.TwemojiFontFamily

    @classmethod
    def twemojiFont(cls) -> QFont:
        """Returns a QFont object using the Twemoji font family.

        Returns:
            QFont: The Twemoji font.
        """
        return QFont(cls.loadTwemojiFont())
