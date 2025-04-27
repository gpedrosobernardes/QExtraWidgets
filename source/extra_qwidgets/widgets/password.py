import qtawesome
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
        self.hide_button = QThemeResponsiveButton()
        self.hide_button.setFlat(True)
        layout.addWidget(self.hide_button)
        self.hide_button.clicked.connect(
            lambda: self.set_password_hide(not self.is_password_hide())
        )
        self.set_password_hide(True)

    def is_password_hide(self) -> bool:
        """
        Returns if the password is hidden.
        :return: bool
        """
        return self.line_edit.echoMode() == QLineEdit.EchoMode.Password

    def set_password_hide(self, hide: bool):
        """
        Sets if the password is hidden.
        :param hide: bool
        :return: None
        """
        if hide:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.hide_button.setIcon(qtawesome.icon("fa6s.eye"))
        else:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.hide_button.setIcon(qtawesome.icon("fa6s.eye-slash"))
