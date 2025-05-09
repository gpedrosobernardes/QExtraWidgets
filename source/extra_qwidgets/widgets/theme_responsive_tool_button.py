from PySide6.QtWidgets import QToolButton

from extra_qwidgets.abc_widgets.abc_theme_responsive import ABCThemeResponsive


class QThemeResponsiveToolButton(QToolButton, ABCThemeResponsive):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ABCThemeResponsive.__init__(self)