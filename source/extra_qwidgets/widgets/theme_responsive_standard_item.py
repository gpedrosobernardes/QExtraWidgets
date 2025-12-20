from PySide6.QtGui import QStandardItem

from extra_qwidgets.abstract.abc_theme_responsive import AbstractThemeResponsive


class QThemeResponsiveStandardItem(QStandardItem, AbstractThemeResponsive):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        AbstractThemeResponsive.__init__(self)