import qtawesome
from PySide6.QtWidgets import QAbstractButton, QPushButton

from extra_qwidgets.abc_widgets.abc_pager import ABCPager
from extra_qwidgets.widgets.theme_responsive_button import QThemeResponsiveButton


class QPager(ABCPager):
    def _new_page_button(self) -> QAbstractButton:
        return QPushButton()

    def _new_icon_button(self, icon: str) -> QAbstractButton:
        btn = QThemeResponsiveButton()
        btn.setIcon(qtawesome.icon(icon))
        return btn

