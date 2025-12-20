from PySide6.QtCore import QSize
from PySide6.QtWidgets import QMenu, QWidget
from qfluentwidgets import SearchLineEdit, SubtitleLabel, RoundMenu

from extra_qwidgets.abstract.emoji_picker import AbstractEmojiPicker
from extra_qwidgets.fluent_widgets.collapse_group import CollapseGroup
from extra_qwidgets.fluent_widgets.theme_responsive_transparent_tool_button import ThemeResponsiveTransparentToolButton


class EmojiPicker(AbstractEmojiPicker):
    def _new_emoji_label(self) -> SubtitleLabel:
        return SubtitleLabel()

    def _new_search_line_edit(self) -> SearchLineEdit:
        return SearchLineEdit()

    def _new_shortcut_button(self) -> ThemeResponsiveTransparentToolButton:
        shortcut_button = ThemeResponsiveTransparentToolButton()
        shortcut_button.setFixedSize(QSize(30, 30))
        shortcut_button.setIconSize(QSize(22, 22))
        return shortcut_button

    def _new_collapse_group(self) -> CollapseGroup:
        return CollapseGroup()

    def _new_menu(self) -> QMenu:
        return RoundMenu()