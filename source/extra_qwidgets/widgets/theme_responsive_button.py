from PySide6.QtWidgets import QPushButton, QApplication

from extra_qwidgets.utils import colorize_icon_by_theme


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
        super().setIcon(colorize_icon_by_theme(icon))