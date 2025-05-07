import qtawesome
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLineEdit

from extra_qwidgets.widgets.theme_responsive_button import QThemeResponsiveButton


class QPassword(QFrame):
    def __init__(self):
        """
        A password input widget with a hide button.
        """
        super().__init__()
        layout = QHBoxLayout(self)
        self.line_edit = QLineEdit()
        layout.addWidget(self.line_edit)
        icon = QIcon()
        icon.addPixmap(qtawesome.icon("fa6s.eye").pixmap(24, 24), state=QIcon.State.On)
        icon.addPixmap(qtawesome.icon("fa6s.eye-slash").pixmap(24, 24), state=QIcon.State.Off)
        self.hide_button = QThemeResponsiveButton()
        self.hide_button.setCheckable(True)
        self.hide_button.setFlat(True)
        self.hide_button.setIcon(icon)
        layout.addWidget(self.hide_button)
        self.hide_button.toggled.connect(self.setPasswordHidden)
        self.setPasswordHidden(True)

    def isPasswordHidden(self) -> bool:
        """
        Returns if the password is hidden.
        :return: bool
        """
        return self.line_edit.echoMode() == QLineEdit.EchoMode.Password

    def setPasswordHidden(self, hide: bool):
        """
        Sets if the password is hidden.
        :param hide: bool
        :return: None
        """
        if hide:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        else:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
