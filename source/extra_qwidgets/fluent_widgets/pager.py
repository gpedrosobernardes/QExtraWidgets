import qtawesome
from PySide6.QtCore import QSize
from qfluentwidgets import PushButton, ToolButton, ToggleButton

from extra_qwidgets.abc_widgets.abc_pager import ABCPager


class Pager(ABCPager):
    def _new_page_button(self) -> ToggleButton:
        return ToggleButton()

    def _new_icon_button(self, icon: str) -> ToolButton:
        tool_button = ToolButton()
        tool_button.setIcon(qtawesome.icon(icon))
        tool_button.setIconSize(QSize(19, 19))
        return tool_button