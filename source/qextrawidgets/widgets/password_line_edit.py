from PySide6.QtGui import QAction
from PySide6.QtWidgets import QLineEdit, QWidget

from qextrawidgets.icons.theme_responsive_icon import QThemeResponsiveIcon


class QPasswordLineEdit(QLineEdit):
    """A line edit widget for passwords with a built-in toggle button to show/hide the text."""

    def __init__(self, parent: QWidget = None) -> None:
        """Initializes the password line edit.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._action = QAction("&Hide/show", self)
        self._action.setCheckable(True)
        self._action.toggled.connect(self.setPasswordHidden)
        self.addAction(self._action, QLineEdit.ActionPosition.TrailingPosition)
        self.setPasswordHidden(True)

    def isPasswordHidden(self) -> bool:
        """Checks if the password is currently hidden (EchoMode.Password).

        Returns:
            bool: True if hidden, False otherwise.
        """
        return self.echoMode() == QLineEdit.EchoMode.Password

    def setPasswordHidden(self, hide: bool) -> None:
        """Sets whether the password should be hidden or visible.

        Args:
            hide (bool): True to hide the password, False to show it.
        """
        if hide:
            self.setEchoMode(QLineEdit.EchoMode.Password)
            self._action.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.eye"))
        else:
            self.setEchoMode(QLineEdit.EchoMode.Normal)
            self._action.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.eye-slash"))
