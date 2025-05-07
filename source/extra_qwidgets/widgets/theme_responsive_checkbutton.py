from extra_qwidgets.widgets.theme_responsive_button import QThemeResponsiveButton


class QThemeResponsiveCheckButton(QThemeResponsiveButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
