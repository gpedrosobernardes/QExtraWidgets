from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QToolButton, QSizePolicy


class QFilterToolButton(QToolButton):
    __font = QFont()
    __font.setPointSize(10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setFont(self.__font)