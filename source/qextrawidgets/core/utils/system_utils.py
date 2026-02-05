from PySide6.QtGui import QGuiApplication, Qt
from PySide6.QtWidgets import QApplication


class QSystemUtils:
    """Utilitários relacionados ao sistema e configurações da aplicação."""

    @staticmethod
    def isDarkMode() -> bool:
        """
        Verifica se a aplicação está rodando em modo escuro.

        Returns:
            bool: True se o modo escuro estiver ativo, False caso contrário.
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
