from typing import Optional, Any, Set

from PySide6.QtCore import Qt, QRect, QModelIndex, QPersistentModelIndex, Signal, QTimer
from PySide6.QtGui import QPalette, QPainter, QIcon, QPixmap, QImage
from PySide6.QtWidgets import (
    QStyleOptionViewItem,
    QStyle,
    QStyledItemDelegate,
    QApplication
)

from qextrawidgets.items.emoji_category_item import QEmojiCategoryItem


class QGroupedIconDelegate(QStyledItemDelegate):
    """
    Delegate for the AccordionGridView.
    Renders categories as horizontal bars with expansion arrows and child items
    as rounded grid cells containing ONLY icons or pixmaps.

    Implements lazy loading signals for missing images.

    Attributes:
        requestImage (Signal): Emitted when an item needs an image loaded.
                               Sends QPersistentModelIndex.
        _arrow_icon (QIcon): Icon used for the expansion indicator.
        _requested_indices (Set[QPersistentModelIndex]): Cache of indices that already requested an image.
    """

    # Signal emitted when an item has no DecorationRole data
    requestImage = Signal(QPersistentModelIndex)

    def __init__(self, parent: Optional[Any] = None, arrow_icon: Optional[QIcon] = None):
        super().__init__(parent)
        self._arrow_icon: QIcon = arrow_icon if arrow_icon else QIcon()
        self._requested_indices: Set[QPersistentModelIndex] = set()

    def setArrowIcon(self, icon: QIcon) -> None:
        self._arrow_icon = icon

    def arrowIcon(self) -> QIcon:
        return self._arrow_icon

    def forceReloadAll(self) -> None:
        """
        Clears the cache of ALL requested images.
        The next time the view paints a missing image item (e.g. on scroll or hover),
        it will emit requestImage again.
        """
        self._requested_indices.clear()

    def forceReload(self, index: QModelIndex):
        persistent_index = QPersistentModelIndex(index)
        if persistent_index in self._requested_indices:
            self._requested_indices.remove(persistent_index)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()

        is_category = not index.parent().isValid()

        if is_category:
            self._draw_category(painter, option, index)
        else:
            self._draw_grid_item(painter, option, index)

        painter.restore()

    # noinspection PyUnresolvedReferences
    def _draw_category(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        style = option.widget.style() if option.widget else QApplication.style()
        palette = option.palette

        if option.state & QStyle.State.State_MouseOver:
            bg_color = palette.color(QPalette.ColorRole.Button).lighter(110)
        else:
            bg_color = palette.color(QPalette.ColorRole.Button)

        painter.fillRect(option.rect, bg_color)
        painter.setPen(palette.color(QPalette.ColorRole.Mid))
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

        is_expanded = index.data(QEmojiCategoryItem.ExpansionStateRole)

        left_padding = 5
        element_spacing = 5
        arrow_size = 20
        user_icon_size = 20
        current_x = option.rect.left() + left_padding
        center_y = option.rect.top() + (option.rect.height() - arrow_size) // 2

        # Draw Arrow
        arrow_rect = QRect(current_x, center_y, arrow_size, arrow_size)
        if not self._arrow_icon.isNull():
            state = QIcon.State.On if is_expanded else QIcon.State.Off
            mode = QIcon.Mode.Disabled if not (option.state & QStyle.State.State_Enabled) else QIcon.Mode.Normal
            self._arrow_icon.paint(painter, arrow_rect, Qt.AlignmentFlag.AlignCenter, mode, state)
        else:
            arrow_opt = QStyleOptionViewItem(option)
            arrow_opt.rect = arrow_rect
            primitive = (
                QStyle.PrimitiveElement.PE_IndicatorArrowDown
                if is_expanded
                else QStyle.PrimitiveElement.PE_IndicatorArrowRight
            )
            style.drawPrimitive(primitive, arrow_opt, painter, option.widget)

        current_x += arrow_size + element_spacing

        # Draw Category Icon
        user_icon = index.data(Qt.ItemDataRole.DecorationRole)
        if isinstance(user_icon, QIcon) and not user_icon.isNull():
            icon_rect = QRect(current_x, center_y, user_icon_size, user_icon_size)
            mode = QIcon.Mode.Disabled if not (option.state & QStyle.State.State_Enabled) else QIcon.Mode.Normal
            user_icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter, mode, QIcon.State.Off)
            current_x += user_icon_size + element_spacing

        # Draw Text
        text_rect = QRect(
            current_x,
            option.rect.top(),
            option.rect.right() - current_x - 5,
            option.rect.height()
        )
        painter.setPen(palette.color(QPalette.ColorRole.ButtonText))
        font = option.font
        font.setBold(True)
        painter.setFont(font)
        text = str(index.data(Qt.ItemDataRole.DisplayRole))
        style.drawItemText(
            painter,
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            palette,
            True,
            text
        )

    # noinspection PyUnresolvedReferences
    def _draw_grid_item(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """
        Draws the child item. Checks for DecorationRole; if missing, triggers requestImage.
        """
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        palette = option.palette
        bg_color = None
        base_bg_color = palette.color(QPalette.ColorRole.Base)

        # Determine Background Color for Selection/Hover
        if option.state & QStyle.State.State_Selected:
            bg_color = palette.color(QPalette.ColorRole.Highlight)
        elif option.state & QStyle.State.State_MouseOver:
            bg_color = base_bg_color.lighter(120)

        # Draw Background (Rounded Rect)
        rect = option.rect.adjusted(2, 2, -2, -2)

        if bg_color is not None:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            painter.drawRoundedRect(rect, 8.0, 8.0)

        # Retrieve Data
        item_data = index.data(Qt.ItemDataRole.DecorationRole)
        target_rect = rect.adjusted(4, 4, -4, -4)

        # --- Lazy Loading Logic ---
        # If no valid data is found, trigger the signal
        is_data_valid = False
        if item_data is not None:
            if isinstance(item_data, QIcon) and not item_data.isNull():
                is_data_valid = True
            elif isinstance(item_data, (QPixmap, QImage)) and not item_data.isNull():
                is_data_valid = True

        # Check if we already requested this index to avoid spamming the signal in the paint loop
        p_index = QPersistentModelIndex(index)
        if p_index not in self._requested_indices:
            self._requested_indices.add(p_index)
            # Emit asynchronously to not block painting
            QTimer.singleShot(0, lambda: self.requestImage.emit(p_index))

        if not is_data_valid:
            # Optional: Draw a placeholder (e.g., a simple loading circle or gray box)
            painter.setPen(Qt.PenStyle.DotLine)
            painter.setPen(palette.color(QPalette.ColorRole.Mid))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(target_rect, 4, 4)

        else:
            # --- Drawing Logic ---
            if isinstance(item_data, QIcon):
                mode = QIcon.Mode.Normal
                if not (option.state & QStyle.State.State_Enabled):
                    mode = QIcon.Mode.Disabled
                elif option.state & QStyle.State.State_Selected:
                    mode = QIcon.Mode.Selected

                item_data.paint(painter, target_rect, Qt.AlignmentFlag.AlignCenter, mode, QIcon.State.Off)

            elif isinstance(item_data, (QPixmap, QImage)):
                if isinstance(item_data, QImage):
                    pixmap = QPixmap.fromImage(item_data)
                else:
                    pixmap = item_data

                scaled_pixmap = pixmap.scaled(
                    target_rect.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                x = target_rect.x() + (target_rect.width() - scaled_pixmap.width()) // 2
                y = target_rect.y() + (target_rect.height() - scaled_pixmap.height()) // 2

                if not (option.state & QStyle.State.State_Enabled):
                    painter.setOpacity(0.5)

                painter.drawPixmap(x, y, scaled_pixmap)

        painter.restore()