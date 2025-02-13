from PySide6.QtWidgets import QFrame, QHBoxLayout, QLineEdit

from extra_qwidgets.widgets.theme_responsive_button import QThemeResponsiveButton
from extra_qwidgets.utils import get_awesome_icon


class QPassword(QFrame):
    def __init__(self):
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
        return self.line_edit.echoMode() == QLineEdit.EchoMode.Password

    def set_password_hide(self, hide: bool):
        if hide:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.hide_button.setIcon(get_awesome_icon("eye"))
        else:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.hide_button.setIcon(get_awesome_icon("eye-slash"))
