from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, QFontDatabase, QFontMetrics
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