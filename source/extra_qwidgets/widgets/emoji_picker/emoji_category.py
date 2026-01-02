from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolButton

from extra_qwidgets.widgets.accordion_item import QAccordionItem
from extra_qwidgets.widgets.emoji_picker.emoji_grid import QEmojiGrid


class EmojiCategory:
    def __init__(self, name: str, text: str, icon: QIcon):
        self._name = name
        self._shortcut = self._create_shortcut_button(text, icon)
        self._grid = QEmojiGrid()
        self._accordion_item = QAccordionItem(text, self._grid)
        self._accordion_item.setObjectName(name)

    def accordionItem(self) -> QAccordionItem:
        return self._accordion_item

    def grid(self) -> QEmojiGrid:
        return self._grid

    def name(self) -> str:
        return self._name

    def shortcut(self) -> QToolButton:
        return self._shortcut

    def deleteLater(self):
        self._grid.deleteLater()
        self._accordion_item.deleteLater()
        self._shortcut.deleteLater()

    @staticmethod
    def _create_shortcut_button(text: str, icon: QIcon) -> QToolButton:
        btn = QToolButton()
        btn.setCheckable(True)
        btn.setAutoRaise(True)  # Visual flat/limpo
        btn.setFixedSize(32, 32)
        btn.setIconSize(QSize(22, 22))
        btn.setToolTip(text)
        btn.setText(text)
        btn.setIcon(icon)
        return btn