from PySide6.QtGui import QStandardItem

from extra_qwidgets.abc_widgets.abc_theme_responsive import ABCThemeResponsive


class QThemeResponsiveStandardItem(QStandardItem, ABCThemeResponsive):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ABCThemeResponsive.__init__(self)