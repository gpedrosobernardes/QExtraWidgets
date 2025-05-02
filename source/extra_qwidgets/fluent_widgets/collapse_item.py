from PySide6.QtCore import QSize
from PySide6.QtWidgets import QAbstractButton
from qfluentwidgets import TransparentToolButton

from extra_qwidgets.abc_widgets.abc_collapse_item import ABCCollapseItem


class CollapseItem(ABCCollapseItem):
    def _new_collapse_button(self) -> QAbstractButton:
        collapse_button = TransparentToolButton()
        collapse_button.setIconSize(QSize(19, 19))
        return collapse_button