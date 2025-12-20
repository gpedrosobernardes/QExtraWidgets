from PySide6.QtWidgets import QToolButton

from extra_qwidgets.abstract.abc_theme_responsive import AbstractThemeResponsive


class QThemeResponsiveToolButton(QToolButton, AbstractThemeResponsive):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        AbstractThemeResponsive.__init__(self)