from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QToolButton, QSizePolicy, QApplication
from extra_qwidgets.utils import is_dark_mode, colorize_pixmap


class QFilterToolButton(QToolButton):
    __font = QFont()
    __font.setPointSize(10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setFont(self.__font)
        QApplication.styleHints().colorSchemeChanged.connect(self._on_theme_change)

    def _on_theme_change(self):
        self.setIcon(self.icon())

    def setIcon(self, icon):
        pixmap = icon.pixmap(QSize(64, 64))
        if is_dark_mode():
            icon = colorize_pixmap(pixmap, "#FFFFFF")
        else:
            icon = colorize_pixmap(pixmap, "#000000")
        super().setIcon(icon)