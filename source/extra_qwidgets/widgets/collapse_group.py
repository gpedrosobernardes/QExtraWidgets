import typing

from PySide6.QtWidgets import QWidget

from extra_qwidgets.abstract.abc_collapse_group import AbstractCollapseGroup
from extra_qwidgets.abstract.abc_collapse_item import ABCCollapseItem
from extra_qwidgets.widgets.collapse_item import QCollapseItem


class QCollapseGroup(AbstractCollapseGroup):
    def _new_collapse_item(self, title: str, widget: QWidget, collapsed: bool = False, name: typing.Optional[str] = None) -> ABCCollapseItem:
        return QCollapseItem(title, widget, collapsed, name)