from PySide6.QtGui import QColor, QColorConstants


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
