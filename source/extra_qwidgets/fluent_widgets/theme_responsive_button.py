from qfluentwidgets import PushButton

from extra_qwidgets.abstract.abc_theme_responsive import AbstractThemeResponsive


class ThemeResponsiveButton(PushButton, AbstractThemeResponsive):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        AbstractThemeResponsive.__init__(self)