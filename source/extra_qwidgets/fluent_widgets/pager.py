import qtawesome
from PySide6.QtCore import QSize
from qfluentwidgets import ToolButton, ToggleButton

from extra_qwidgets.abstract.abc_pager import ABCPager
from extra_qwidgets.fluent_widgets.theme_responsive_tool_button import ThemeResponsiveToolButton


class Pager(ABCPager):
    def _new_page_button(self) -> ToggleButton:
        return ToggleButton()

    def _new_icon_button(self, icon: str) -> ToolButton:
        tool_button = ThemeResponsiveToolButton()
        tool_button.setIcon(qtawesome.icon(icon))
        tool_button.setIconSize(QSize(19, 19))
        return tool_button