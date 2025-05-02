from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication

from extra_qwidgets.proxys import is_dark_mode, colorize_icon


class QThemeResponsiveAction(QAction):
    def __init__(self, *args, **kwargs):
        """
        A QAction that changes its icon color based on the current theme.
        :param args: QAction's arguments
        :param kwargs: QAction's keyword arguments
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