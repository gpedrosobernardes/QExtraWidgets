from PySide6.QtGui import QGuiApplication, Qt
from PySide6.QtWidgets import QApplication


class QSystemUtils:
    """Utilities related to system and application settings."""

    @staticmethod
    def isDarkMode() -> bool:
        """
        Checks if the application is running in dark mode.

        Returns:
            bool: True if dark mode is active, False otherwise.
        """
        style_hints = QApplication.styleHints()
        color_scheme = style_hints.colorScheme()
        return color_scheme.value == 2

    @staticmethod
    def applyDarkMode():
        """Applies a generic dark palette."""
        QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Dark)

    @staticmethod
    def applyLightMode():
        """Restores the default system palette (Light)."""
        # Using the default Fusion style palette is usually a clean light palette
        QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)
