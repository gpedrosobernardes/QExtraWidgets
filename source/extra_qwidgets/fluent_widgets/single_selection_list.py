import qtawesome
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QListWidget, QAbstractButton
from qfluentwidgets import ListWidget

from extra_qwidgets.abstract.abc_single_selection_list import ABCSingleSelectionList
from extra_qwidgets.fluent_widgets.theme_responsive_transparent_tool_button import ThemeResponsiveTransparentToolButton


class SingleSelectionList(ABCSingleSelectionList):
    def _new_tool_button(self, icon: str) -> QAbstractButton:
        tool_button = ThemeResponsiveTransparentToolButton()
        tool_button.setIcon(qtawesome.icon(icon))
        tool_button.setIconSize(QSize(19, 19))
        return tool_button

    def _new_list_widget(self) -> QListWidget:
        return ListWidget()