from PySide6.QtWidgets import QPushButton, QApplication
from extra_qwidgets.utils import is_dark_mode, colorize_icon


class QThemeResponsiveButton(QPushButton):
    def __init__(self, *args, **kwargs):
        """
        A QPushButton that changes its icon color based on the current theme.
        :param args: QPushButton's arguments
        :param kwargs: QPushButton's keyword arguments
        """
        super().__init__(*args, **kwargs)
        QApplication.styleHints().colorSchemeChanged.connect(self._on_theme_change)

    def _on_theme_change(self):
        self.setIcon(self.icon())

    def setIcon(self, icon):
        if is_dark_mode():
            icon = colorize_icon(icon, "#FFFFFF")
        else:
            icon = colorize_icon(icon, "#000000")
        super().setIcon(icon)