from PySide6.QtWidgets import QPushButton

from extra_qwidgets.abc_widgets.abc_theme_responsive import ABCThemeResponsive


class QThemeResponsiveButton(QPushButton, ABCThemeResponsive):
    def __init__(self, *args, **kwargs):
        """
        A QPushButton that changes its icon color based on the current theme.
        :param args: QPushButton's arguments
        :param kwargs: QPushButton's keyword arguments
        """
        super().__init__(*args, **kwargs)
        ABCThemeResponsive.__init__(self)