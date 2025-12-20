from qfluentwidgets import TransparentToggleToolButton

from extra_qwidgets.abstract.theme_responsive import AbstractThemeResponsive


class ThemeResponsiveTransparentToggleToolButton(TransparentToggleToolButton, AbstractThemeResponsive):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)