import typing

import emoji_data_python
from PySide6.QtCore import QModelIndex, Qt, QPoint, QSize
from PySide6.QtGui import QPainter, QPalette, QFontMetrics
from PySide6.QtWidgets import (
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QStyle,
)

from qextrawidgets.emoji_utils import EmojiImageProvider


class QStandardTwemojiDelegate(QStyledItemDelegate):
    """Delegate that renders text with inline Twemoji images support.

    It automatically detects Unicode emojis in the text and replaces them with
    high-quality Twemoji images while maintaining text alignment.
    """

    EmojiRegex = emoji_data_python.get_emoji_regex()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """Renders the delegate using the given painter and style option.

        Args:
            painter (QPainter): The painter to use.
            option (QStyleOptionViewItem): The style option.
            index (QModelIndex): The model index.
        """
        painter.save()

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        widget = getattr(opt, "widget")

        style = widget.style()

        # Draws background, selection, focus, etc.
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, option, painter, getattr(option, "widget"))

        # ===== data =====
        text: str = getattr(opt, "text")
        fm: QFontMetrics = getattr(opt, "fontMetrics")
        alignment: Qt.AlignmentFlag = getattr(opt, "displayAlignment")
        palette: QPalette = getattr(opt, "palette")
        state: QStyle.StateFlag = getattr(opt, "state")

        painter.setPen(
            palette.color(
                QPalette.ColorRole.HighlightedText
                if state & QStyle.StateFlag.State_Selected
                else QPalette.ColorRole.Text
            )
        )

        # ===== real text area =====
        text_rect = style.subElementRect(
            QStyle.SubElement.SE_ItemViewItemText, opt, widget
        )

        blocks = self.get_text_blocks(text)

        # ===== total width =====
        emoji_size = fm.ascent()
        total_width = 0
        for block in blocks:
            if self.EmojiRegex.match(block):
                total_width += emoji_size
            else:
                total_width += fm.horizontalAdvance(block)

        # ===== horizontal alignment =====
        if alignment & Qt.AlignmentFlag.AlignHCenter:
            offset_x = max((text_rect.width() - total_width) // 2, 0)
        elif alignment & Qt.AlignmentFlag.AlignRight:
            offset_x = max(text_rect.width() - total_width, 0)
        else:
            offset_x = 0

        # ===== vertical alignment =====
        font_height = fm.height()

        if alignment & Qt.AlignmentFlag.AlignTop:
            base_y = text_rect.top() + fm.ascent()
            img_y = text_rect.top()
        elif alignment & Qt.AlignmentFlag.AlignBottom:
            base_y = text_rect.bottom() - fm.descent()
            img_y = text_rect.bottom() - font_height
        else:
            base_y = (
                text_rect.top()
                + (text_rect.height() - font_height) // 2
                + fm.ascent()
            )
            img_y = (
                text_rect.top()
                + (text_rect.height() - font_height) // 2
            )

        text_cursor = QPoint(text_rect.left() + offset_x, base_y)
        image_cursor = QPoint(text_rect.left() + offset_x, img_y)

        # ===== drawing =====
        for block in blocks:
            if self.EmojiRegex.match(block):
                pixmap = EmojiImageProvider.getPixmap(
                    block,
                    0,
                    emoji_size,
                    painter.device().devicePixelRatio(),
                )
                painter.drawPixmap(image_cursor, pixmap)
                advance = emoji_size
            else:
                painter.drawText(text_cursor, block)
                advance = fm.horizontalAdvance(block)

            text_cursor.setX(text_cursor.x() + advance)
            image_cursor.setX(image_cursor.x() + advance)

        painter.restore()

    @classmethod
    def get_text_blocks(cls, text: str) -> typing.List[str]:
        """Splits the text into blocks of plain text and individual emojis.

        Args:
            text (str): The input text containing mixed content.

        Returns:
            List[str]: A list of strings where each element is either plain text or a single emoji.
        """
        return cls.EmojiRegex.split(text)
