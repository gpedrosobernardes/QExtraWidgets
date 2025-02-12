from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QPushButton
from source.extra_qwidgets.utils import is_dark_mode, colorize_icon


class QColorResponsiveButton(QPushButton):
    def __init__(self, parent=None):
        super(QColorResponsiveButton, self).__init__(parent)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.PaletteChange:
            self.setIcon(self.icon())
        return super().eventFilter(obj, event)

    def setIcon(self, icon):
        if is_dark_mode():
            icon = colorize_icon(icon, "#FFFFFF")
        else:
            icon = colorize_icon(icon, "#000000")
        super().setIcon(icon)