from PySide6.QtCore import (
    QObject,
    Qt,
    QRect,
    QModelIndex,
    QPersistentModelIndex,
    Signal,
    QTimer, QSize, QSizeF,
)
from PySide6.QtGui import QPalette, QPainter, QIcon, QPixmap, QImage
from PySide6.QtWidgets import (
    QStyleOptionViewItem,
    QStyle,
    QStyledItemDelegate,
)
import typing

from qextrawidgets.core.utils.system_utils import log_qt_performance


class QGridIconDelegate(QStyledItemDelegate):
    """
    Delegate for a grid view.
    Renders items as rounded grid cells containing ONLY icons or pixmaps.

    Implements lazy loading signals for missing images.

    Attributes:
        requestImage (Signal): Emitted when an item needs an image loaded.
                               Sends QPersistentModelIndex.
        _requested_indices (Set[QPersistentModelIndex]): Cache of indices that already requested an image.
    """

    # Signal emitted when an item has no DecorationRole data
    requestImage = Signal(QPersistentModelIndex, QSize)

    def __init__(
        self,
        parent: typing.Optional[QObject] = None,
        item_internal_margin_ratio: float = 0.1,
    ):
        """
        Initialize the delegate.

        Args:
            parent (Optional[Any]): The parent object.
            item_internal_margin_ratio (float): Internal margin ratio (0.0 to 0.5).
        """
        super().__init__(parent)
        self.setItemInternalMargin(item_internal_margin_ratio)

    def setItemInternalMargin(self, ratio: float) -> None:
        """
        Set the internal margin ratio for the item content.

        Args:
            ratio (float): A value between 0.0 (0%) and 0.5 (50%).
        """
        self._item_internal_margin_ratio = max(0.0, min(0.5, ratio))

    def itemInternalMargin(self) -> float:
        """
        Get the internal margin ratio for the item content.

        Returns:
            float: A value between 0.0 (0%) and 0.5 (50%).
        """
        return self._item_internal_margin_ratio

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QPersistentModelIndex,
    ) -> None:
        """
        Paint the item.

        Args:
            painter (QPainter): The painter object.
            option (QStyleOptionViewItem): Style options for rendering.
            index (QModelIndex): The index of the item being painted.
        """
        painter.save()
        self._draw_grid_item(painter, option, index)
        painter.restore()

    @log_qt_performance
    def _draw_grid_item(
            self,
            painter: QPainter,
            option: QStyleOptionViewItem,
            index: QPersistentModelIndex,
    ) -> None:
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)

        palette = option.palette
        current_state = option.state
        bg_color = None
        base_bg_color = palette.color(QPalette.ColorRole.Base)
        dpr = painter.device().devicePixelRatio()

        # Determine Background Color for Selection/Hover
        if current_state & QStyle.StateFlag.State_Selected:
            bg_color = palette.color(QPalette.ColorRole.Highlight)
        elif current_state & QStyle.StateFlag.State_MouseOver:
            bg_color = base_bg_color.lighter(120)

        # Draw Background (Rounded Rect)
        rect = option.rect.adjusted(2, 2, -2, -2)

        if bg_color is not None:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            painter.drawRoundedRect(rect, 8.0, 8.0)

        # Retrieve Data
        item_data = index.data(Qt.ItemDataRole.DecorationRole)

        margin = int(min(rect.width(), rect.height()) * self._item_internal_margin_ratio)
        target_rect = rect.adjusted(margin, margin, -margin, -margin)
        target_size = target_rect.size()

        # ── Fast path: emoji string direto no DecorationRole ─────────────────────
        # Renderiza com drawText — zero alocação, sem I/O, sem sinal emitido.
        if isinstance(item_data, str) and item_data:

            if not (current_state & QStyle.StateFlag.State_Enabled):
                painter.setOpacity(0.5)

            painter.drawText(target_rect, Qt.AlignmentFlag.AlignCenter, item_data)

            if not (current_state & QStyle.StateFlag.State_Enabled):
                painter.setOpacity(1.0)
            return

        # ── Slow path: QIcon / QPixmap / QImage (carregado pelo provider) ────────
        if not isinstance(item_data, (QIcon, QPixmap, QImage)) or item_data.isNull():
            physical_size = (QSizeF(target_size) * dpr).toSize()
            painter.setPen(palette.color(QPalette.ColorRole.Mid))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(target_rect, 4, 4)
            self.requestImage.emit(index, physical_size)
            return

        # ── QIcon ─────────────────────────────────────────────────────────────────
        if isinstance(item_data, QIcon):
            mode = QIcon.Mode.Normal
            if not (current_state & QStyle.StateFlag.State_Enabled):
                mode = QIcon.Mode.Disabled
            elif current_state & QStyle.StateFlag.State_Selected:
                mode = QIcon.Mode.Selected

            item_data.paint(
                painter,
                target_rect,
                Qt.AlignmentFlag.AlignCenter,
                mode,
                QIcon.State.Off,
            )
            return

        # ── QPixmap / QImage ──────────────────────────────────────────────────────
        if isinstance(item_data, (QPixmap, QImage)):
            logical_size = item_data.deviceIndependentSize().toSize()
            fit_size = logical_size.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatio)

            aligned_rect = QStyle.alignedRect(
                Qt.LayoutDirection.LeftToRight,
                Qt.AlignmentFlag.AlignCenter,
                fit_size,
                target_rect,
            )

            if not (current_state & QStyle.StateFlag.State_Enabled):
                painter.setOpacity(0.5)
                painter.drawPixmap(aligned_rect, item_data)
                painter.setOpacity(1.0)
            else:
                painter.drawPixmap(aligned_rect, item_data)