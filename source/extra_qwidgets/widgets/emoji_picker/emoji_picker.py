from PySide6.QtCore import QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QAbstractButton, QLineEdit, QLabel, QMenu

from extra_qwidgets.abstract.abc_collapse_group import AbstractCollapseGroup
from extra_qwidgets.abstract.emoji_picker.abc_emoji_picker import AbstractEmojiPicker
from extra_qwidgets.widgets.collapse_group import QCollapseGroup
from extra_qwidgets.widgets.theme_responsive_button import QThemeResponsiveButton


class QEmojiPicker(AbstractEmojiPicker):
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
        shortcut_button = QThemeResponsiveButton()
        shortcut_button.setFixedSize(QSize(30, 30))
        shortcut_button.setIconSize(QSize(22, 22))
        shortcut_button.setFlat(True)
        return shortcut_button

    def _new_collapse_group(self) -> AbstractCollapseGroup:
        return QCollapseGroup()

    def _new_menu(self) -> QMenu:
        return QMenu()