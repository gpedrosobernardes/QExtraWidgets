from PySide6.QtWidgets import QAbstractButton

from extra_qwidgets.abc_widgets.abc_collapse_item import ABCCollapseItem
from extra_qwidgets.widgets.theme_responsive_button import QThemeResponsiveButton


class QCollapseItem(ABCCollapseItem):
    def _new_collapse_button(self) -> QAbstractButton:
        collapse_button = QThemeResponsiveButton()
        collapse_button.setFlat(True)
        return collapse_button