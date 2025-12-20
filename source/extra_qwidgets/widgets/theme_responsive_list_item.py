from PySide6.QtWidgets import QListWidgetItem

from extra_qwidgets.abstract.abc_theme_responsive import AbstractThemeResponsive


class QThemeResponsiveListItem(QListWidgetItem, AbstractThemeResponsive):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        AbstractThemeResponsive.__init__(self)