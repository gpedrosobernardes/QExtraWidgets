from PySide6.QtCore import QSize
from qfluentwidgets import TransparentToolButton, SearchLineEdit, SubtitleLabel

from extra_qwidgets.abc_widgets.emoji_picker.abc_emoji_picker import ABCEmojiPicker
from extra_qwidgets.fluent_widgets.collapse_group import CollapseGroup


class EmojiPicker(ABCEmojiPicker):
    def _new_emoji_label(self) -> SubtitleLabel:
        return SubtitleLabel()

    def _new_search_line_edit(self) -> SearchLineEdit:
        return SearchLineEdit()

    def _new_shortcut_button(self) -> TransparentToolButton:
        shortcut_button = TransparentToolButton()
        shortcut_button.setFixedSize(QSize(30, 30))
        shortcut_button.setIconSize(QSize(22, 22))
        return shortcut_button

    def _new_collapse_group(self) -> CollapseGroup:
        return CollapseGroup()