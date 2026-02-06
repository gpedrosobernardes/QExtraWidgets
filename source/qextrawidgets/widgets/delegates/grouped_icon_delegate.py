from PySide6.QtCore import Qt, QRect, QModelIndex, QPersistentModelIndex
from PySide6.QtGui import QPalette, QPainter, QIcon, QFont
from PySide6.QtWidgets import QStyleOptionViewItem, QStyle, QWidget
import typing

from qextrawidgets.widgets.delegates.grid_icon_delegate import QGridIconDelegate


class QGroupedIconDelegate(QGridIconDelegate):
    """
    Delegate for the QGroupedIconView.
    Renders categories as horizontal bars with expansion arrows and child items
    as rounded grid cells containing ONLY icons or pixmaps.

    Implements lazy loading signals for missing images via QGridIconDelegate.
    """

    def __init__(
        self,
        parent: typing.Optional[QWidget] = None,
        arrow_icon: typing.Optional[QIcon] = None,
        item_internal_margin_ratio: float = 0.1,
    ):
        """
        Initialize the delegate.

        Args:
            parent (Optional[Any]): The parent object.
            arrow_icon (Optional[QIcon]): Custom icon for the expansion arrow. If None, uses default primitive.
            item_internal_margin_ratio (float): Internal margin ratio (0.0 to 0.5).
        """
        super().__init__(parent, item_internal_margin_ratio=item_internal_margin_ratio)
        self._arrow_icon: QIcon = arrow_icon if arrow_icon else QIcon()

    def setArrowIcon(self, icon: QIcon) -> None:
        """
        Set the icon used for the expansion indicator.

        Args:
            icon (QIcon): The new arrow icon.
        """
        self._arrow_icon = icon

    def arrowIcon(self) -> QIcon:
        """
        Get the current arrow icon.

        Returns:
            QIcon: The current arrow icon.
        """
        return self._arrow_icon

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: typing.Union[QModelIndex, QPersistentModelIndex],
    ) -> None:
        """
        Paint the item.

        Delegates to _draw_category for category items and _draw_grid_item (from base) for child items.

        Args:
            painter (QPainter): The painter object.
            option (QStyleOptionViewItem): Style options for rendering.
            index (QModelIndex): The index of the item being painted.
        """
        painter.save()

        is_category = not index.parent().isValid()

        if is_category:
            self._draw_category(painter, option, index)
        else:
            self._draw_grid_item(painter, option, index)

        painter.restore()

    def _draw_category(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: typing.Union[QModelIndex, QPersistentModelIndex],
    ) -> None:
        """
        Draw a category header item.

        Renders the background, expansion arrow, icon, and text.

        Args:
            painter (QPainter): The painter object.
            option (QStyleOptionViewItem): The style options.
            index (QModelIndex): The model index of the category.
        """
        widget = typing.cast(QWidget, option.widget)
        style = widget.style()
        palette = typing.cast(QPalette, option.palette)
        current_state = typing.cast(QStyle.StateFlag, option.state)
        option_rect = typing.cast(QRect, option.rect)

        if current_state & QStyle.StateFlag.State_MouseOver:
            bg_color = palette.color(QPalette.ColorRole.Button).lighter(110)
        else:
            bg_color = palette.color(QPalette.ColorRole.Button)

        painter.fillRect(option_rect, bg_color)
        painter.setPen(palette.color(QPalette.ColorRole.Mid))
        painter.drawLine(option_rect.bottomLeft(), option_rect.bottomRight())

        is_expanded = bool(current_state & QStyle.StateFlag.State_Open)

        left_padding = 5
        element_spacing = 5
        arrow_size = 20
        user_icon_size = 20
        current_x = option_rect.left() + left_padding
        center_y = option_rect.top() + (option_rect.height() - arrow_size) // 2

        # Draw Arrow
        arrow_rect = QRect(current_x, center_y, arrow_size, arrow_size)
        if not self._arrow_icon.isNull():
            state = QIcon.State.On if is_expanded else QIcon.State.Off
            mode = (
                QIcon.Mode.Disabled
                if not (current_state & QStyle.StateFlag.State_Enabled)
                else QIcon.Mode.Normal
            )
            self._arrow_icon.paint(
                painter, arrow_rect, Qt.AlignmentFlag.AlignCenter, mode, state
            )
        else:
            arrow_opt = QStyleOptionViewItem(option)
            setattr(arrow_opt, "rect", arrow_rect)
            primitive = (
                QStyle.PrimitiveElement.PE_IndicatorArrowDown
                if is_expanded
                else QStyle.PrimitiveElement.PE_IndicatorArrowRight
            )
            style.drawPrimitive(primitive, arrow_opt, painter, widget)

        current_x += arrow_size + element_spacing

        # Draw Category Icon
        user_icon = index.data(Qt.ItemDataRole.DecorationRole)
        if isinstance(user_icon, QIcon) and not user_icon.isNull():
            icon_rect = QRect(current_x, center_y, user_icon_size, user_icon_size)
            mode = (
                QIcon.Mode.Disabled
                if not (current_state & QStyle.StateFlag.State_Enabled)
                else QIcon.Mode.Normal
            )
            user_icon.paint(
                painter, icon_rect, Qt.AlignmentFlag.AlignCenter, mode, QIcon.State.Off
            )
            current_x += user_icon_size + element_spacing

        # Draw Text
        text_rect = QRect(
            current_x,
            option_rect.top(),
            option_rect.right() - current_x - 5,
            option_rect.height(),
        )
        painter.setPen(palette.color(QPalette.ColorRole.ButtonText))
        font = typing.cast(QFont, option.font)
        font.setBold(True)
        painter.setFont(font)
        text = str(index.data(Qt.ItemDataRole.DisplayRole))
        style.drawItemText(
            painter,
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            palette,
            True,
            text,
        )
