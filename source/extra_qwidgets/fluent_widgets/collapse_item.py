from PySide6.QtCore import QSize

from extra_qwidgets.abc_widgets.abc_collapse_item import ABCCollapseItem
from extra_qwidgets.fluent_widgets.theme_responsive_transparent_toggle_tool_button import \
    ThemeResponsiveTransparentToggleToolButton


class CollapseItem(ABCCollapseItem):
    def _new_collapse_button(self) -> ThemeResponsiveTransparentToggleToolButton:
        collapse_button = ThemeResponsiveTransparentToggleToolButton()
        collapse_button.setIconSize(QSize(19, 19))
        return collapse_button