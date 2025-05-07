from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication

from extra_qwidgets.utils import is_dark_mode, colorize_pixmap


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
            icon = colorize_pixmap(icon, "#FFFFFF")
        else:
            icon = colorize_pixmap(icon, "#000000")
        super().setIcon(icon)