from PySide6.QtGui import QAction
from PySide6.QtWidgets import QLineEdit

from qextrawidgets.icons import QThemeResponsiveIcon


class QPassword(QLineEdit):
    def __init__(self, parent=None):
        super(QPassword, self).__init__(parent)
        self._action = QAction("&Hide/show", self)
        self._action.setCheckable(True)
        self._action.toggled.connect(self.setPasswordHidden)
        self.addAction(self._action, QLineEdit.ActionPosition.TrailingPosition)
        self.setPasswordHidden(True)

    def isPasswordHidden(self) -> bool:
        """
        Returns if the password is hidden.
        :return: bool
        """
        return self.echoMode() == QLineEdit.EchoMode.Password

    def setPasswordHidden(self, hide: bool):
        """
        Sets if the password is hidden.
        :param hide: bool
        :return: None
        """
        if hide:
            self.setEchoMode(QLineEdit.EchoMode.Password)
            self._action.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.eye"))
        else:
            self.setEchoMode(QLineEdit.EchoMode.Normal)
            self._action.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.eye-slash"))
