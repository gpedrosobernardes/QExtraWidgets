from PySide6.QtCore import (
    QObject,
    Qt,
    QRect,
    QModelIndex,
    QPersistentModelIndex,
    Signal,
    QTimer,
)
from PySide6.QtGui import QPalette, QPainter, QIcon, QPixmap, QImage
from PySide6.QtWidgets import (
    QStyleOptionViewItem,
    QStyle,
    QStyledItemDelegate,
)
import typing


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
    requestImage = Signal(QPersistentModelIndex)

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
        self._requested_indices: typing.Set[QPersistentModelIndex] = set()
        self.setItemInternalMargin(item_internal_margin_ratio)

    def setItemInternalMargin(self, ratio: float) -> None:
        """
        Set the internal margin ratio for the item content.

        Args:
            ratio (float): A value between 0.0 (0%) and 0.5 (50%).
        """
        self._item_internal_margin_ratio = max(0.0, min(0.5, ratio))

    def forceReloadAll(self) -> None:
        """
        Clear the cache of ALL requested images.

        The next time the view paints a missing image item (e.g. on scroll or hover),
        it will emit requestImage again.
        """
        self._requested_indices.clear()

    def forceReload(self, index: QModelIndex) -> None:
        """
        Clear the cache for a specific index to force re-requesting the image.

        Args:
            index (QModelIndex): The index to clear from the cache.
        """
        persistent_index = QPersistentModelIndex(index)
        if persistent_index in self._requested_indices:
            self._requested_indices.remove(persistent_index)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: typing.Union[QModelIndex, QPersistentModelIndex],
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

    def _draw_grid_item(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: typing.Union[QModelIndex, QPersistentModelIndex],
    ) -> None:
        """
        Draw a child item in the grid used for lazy loading check.

        Checks for DecorationRole; if missing, triggers requestImage signal.
        Renders the icon or pixmap centered in the item rect.

        Args:
            painter (QPainter): The painter object.
            option (QStyleOptionViewItem): The style options.
            index (QModelIndex): The model index of the item.
        """

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        palette = typing.cast(QPalette, option.palette)
        current_state = typing.cast(QStyle.StateFlag, option.state)
        bg_color = None
        base_bg_color = palette.color(QPalette.ColorRole.Base)

        # Determine Background Color for Selection/Hover
        if current_state & QStyle.StateFlag.State_Selected:
            bg_color = palette.color(QPalette.ColorRole.Highlight)
        elif current_state & QStyle.StateFlag.State_MouseOver:
            bg_color = base_bg_color.lighter(120)

        # Draw Background (Rounded Rect)
        rect = typing.cast(QRect, option.rect).adjusted(2, 2, -2, -2)

        if bg_color is not None:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            painter.drawRoundedRect(rect, 8.0, 8.0)

        # Retrieve Data
        item_data = index.data(Qt.ItemDataRole.DecorationRole)

        margin = int(
            min(rect.width(), rect.height()) * self._item_internal_margin_ratio
        )
        target_rect = rect.adjusted(margin, margin, -margin, -margin)

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

            elif isinstance(item_data, (QPixmap, QImage)):
                if isinstance(item_data, QImage):
                    pixmap = QPixmap.fromImage(item_data)
                else:
                    pixmap = item_data

                scaled_pixmap = pixmap.scaled(
                    target_rect.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )

                x = target_rect.x() + (target_rect.width() - scaled_pixmap.width()) // 2
                y = (
                    target_rect.y()
                    + (target_rect.height() - scaled_pixmap.height()) // 2
                )

                if not (current_state & QStyle.StateFlag.State_Enabled):
                    painter.setOpacity(0.5)

                painter.drawPixmap(x, y, scaled_pixmap)
