from extra_qwidgets.widgets import QThemeResponsiveButton


class QThemeResponsiveCheckButton(QThemeResponsiveButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
