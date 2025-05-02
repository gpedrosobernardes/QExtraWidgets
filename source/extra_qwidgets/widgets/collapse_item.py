from PySide6.QtWidgets import QPushButton, QAbstractButton

from extra_qwidgets.abc_widgets.abc_collapse_item import ABCCollapseItem


class QCollapseItem(ABCCollapseItem):
    def _new_collapse_button(self) -> QAbstractButton:
        collapse_button = QPushButton()
        collapse_button.setFlat(True)
        return collapse_button