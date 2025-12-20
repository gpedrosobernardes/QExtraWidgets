from qfluentwidgets import TransparentToolButton

from extra_qwidgets.abstract.theme_responsive import AbstractThemeResponsive


class ThemeResponsiveTransparentToolButton(TransparentToolButton, AbstractThemeResponsive):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        AbstractThemeResponsive.__init__(self)