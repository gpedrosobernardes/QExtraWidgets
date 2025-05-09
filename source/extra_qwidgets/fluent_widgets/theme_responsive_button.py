from qfluentwidgets import PushButton

from extra_qwidgets.abc_widgets.abc_theme_responsive import ABCThemeResponsive


class ThemeResponsiveButton(PushButton, ABCThemeResponsive):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ABCThemeResponsive.__init__(self)