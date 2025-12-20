import typing

from PySide6.QtWidgets import QWidget

from extra_qwidgets.abstract.collapse_group import AbstractCollapseGroup
from extra_qwidgets.abstract.collapse_item import AbstractCollapseItem
from extra_qwidgets.fluent_widgets.collapse_item import CollapseItem


class CollapseGroup(AbstractCollapseGroup):
    def _new_collapse_item(self, title: str, widget: QWidget, collapsed: bool = False, name: typing.Optional[str] = None) -> AbstractCollapseItem:
        return CollapseItem(title, widget, collapsed, name)