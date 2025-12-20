from PySide6.QtWidgets import QPushButton

from extra_qwidgets.abstract.theme_responsive import AbstractThemeResponsive


class QThemeResponsiveButton(QPushButton, AbstractThemeResponsive):
    def __init__(self, *args, **kwargs):
        """
        A QPushButton that changes its icon color based on the current theme.
        :param args: QPushButton's arguments
        :param kwargs: QPushButton's keyword arguments
        """
        super().__init__(*args, **kwargs)
        AbstractThemeResponsive.__init__(self)