from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle

from extra_qwidgets.emoji_utils import EmojiImageProvider


class EmojiDelegate(QStyledItemDelegate):
    """
    Renders the Emoji. If it's an image, draws the Pixmap.
    If it's font, draws the text. This saves memory compared to creating QIcons.
    """

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        if not index.isValid():
            return

        painter.save()

        state = getattr(option, "state")
        rect = getattr(option, "rect")
        palette = getattr(option, "palette")

        # 1. Draw background (hover/selection)
        if state & QStyle.StateFlag.State_Selected:
            painter.fillRect(rect, palette.highlight())
        elif state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(rect, palette.midlight())

        # 2. Get Emoji data
        # Assuming you stored the file path or code in UserRole
        emoji_data = index.data(Qt.ItemDataRole.UserRole)

        # 3. Define the rectangle where the icon will be drawn (with padding)
        icon_rect = getattr(option, "rect")
        icon_rect_adjusted = icon_rect.adjusted(4, 4, -4, -4)

        pixmap = EmojiImageProvider.get_pixmap(
            emoji_data,
            icon_rect_adjusted.size(),
            painter.device().devicePixelRatio()
        )

        # 4. Draw
        if not pixmap.isNull():
            # Center
            # Since pixmap has devicePixelRatio configured, we use logical dimensions (divided by dpr) to align
            logical_w = pixmap.width() / pixmap.devicePixelRatio()
            logical_h = pixmap.height() / pixmap.devicePixelRatio()

            x = icon_rect_adjusted.x() + (icon_rect_adjusted.width() - logical_w) / 2
            y = icon_rect_adjusted.y() + (icon_rect_adjusted.height() - logical_h) / 2

            painter.drawPixmap(int(x), int(y), pixmap)

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(40, 40)  # Fixed size for performance
