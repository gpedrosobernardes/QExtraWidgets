from PySide6.QtCore import QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPushButton, QAbstractButton, QLineEdit, QLabel

from extra_qwidgets.abc_widgets.abc_collapse_group import ABCCollapseGroup
from extra_qwidgets.abc_widgets.emoji_picker.abc_emoji_picker import ABCEmojiPicker
from extra_qwidgets.widgets import QCollapseGroup


class QEmojiPicker(ABCEmojiPicker):
    def _new_emoji_label(self) -> QLabel:
        font = QFont()
        font.setBold(True)
        font.setPointSize(13)
        label = QLabel()
        label.setFont(font)
        return label

    def _new_search_line_edit(self) -> QLineEdit:
        font = QFont()
        font.setPointSize(12)
        line_edit = QLineEdit()
        line_edit.setFont(font)
        return line_edit

    def _new_shortcut_button(self) -> QAbstractButton:
        shortcut_button = QPushButton()
        shortcut_button.setFixedSize(QSize(30, 30))
        shortcut_button.setIconSize(QSize(22, 22))
        shortcut_button.setFlat(True)
        return shortcut_button

    def _new_collapse_group(self) -> ABCCollapseGroup:
        return QCollapseGroup()