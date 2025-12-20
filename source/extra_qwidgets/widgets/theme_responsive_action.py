from PySide6.QtGui import QAction

from extra_qwidgets.abstract.abc_theme_responsive import AbstractThemeResponsive


class QThemeResponsiveAction(QAction, AbstractThemeResponsive):
    def __init__(self, *args, **kwargs):
        """
        A QAction that changes its icon color based on the current theme.
        :param args: QAction's arguments
        :param kwargs: QAction's keyword arguments
        """
        super().__init__(*args, **kwargs)
        AbstractThemeResponsive.__init__(self)