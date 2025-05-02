import typing

from PySide6.QtWidgets import QWidget

from extra_qwidgets.abc_widgets.abc_collapse_group import ABCCollapseGroup
from extra_qwidgets.abc_widgets.abc_collapse_item import ABCCollapseItem
from extra_qwidgets.fluent_widgets.collapse_item import CollapseItem


class CollapseGroup(ABCCollapseGroup):
    def _new_collapse_item(self, title: str, widget: QWidget, collapsed: bool = False, name: typing.Optional[str] = None) -> ABCCollapseItem:
        return CollapseItem(title, widget, collapsed, name)