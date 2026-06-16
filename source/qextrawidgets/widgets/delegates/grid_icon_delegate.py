from PySide6.QtCore import (
    Qt,
    QModelIndex,
    QPersistentModelIndex,
    Signal,
    QSize,
    QSizeF,
)
from PySide6.QtGui import QPalette, QPainter, QIcon, QPixmap
from PySide6.QtWidgets import (
    QStyleOptionViewItem,
    QStyle,
    QStyledItemDelegate,
)

from qextrawidgets.core.utils.system_utils import log_qt_performance


class QGridIconDelegate(QStyledItemDelegate):
    requestImage = Signal(QPersistentModelIndex, QSize)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex,
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
            index: QModelIndex,
    ) -> None:
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        view = option.widget.parent()
        padding = view.padding()

        bg_color = None

        if option.state & QStyle.StateFlag.State_Selected:
            bg_color = option.palette.color(QPalette.ColorRole.Highlight)
        elif option.state & QStyle.StateFlag.State_MouseOver:
            bg_color = option.palette.color(QPalette.ColorRole.Base).lighter(120)

        if bg_color is not None:
            painter.setBrush(bg_color)
            painter.drawRoundedRect(option.rect, 8.0, 8.0)

        item_data = index.data(Qt.ItemDataRole.DecorationRole)

        if not isinstance(item_data, (QIcon, QPixmap)) or item_data.isNull():
            dpr = painter.device().devicePixelRatio()
            physical_size = (QSizeF(option.rect.size()) * dpr).toSize()
            painter.setPen(option.palette.color(QPalette.ColorRole.Mid))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(option.rect, 4, 4)
            self.requestImage.emit(index, physical_size)

        elif isinstance(item_data, QIcon):
            icon_rect = option.rect.adjusted(padding, padding, -padding, -padding)

            mode = QIcon.Mode.Normal
            if not (option.state & QStyle.StateFlag.State_Enabled):
                mode = QIcon.Mode.Disabled
            elif option.state & QStyle.StateFlag.State_Selected:
                mode = QIcon.Mode.Selected

            item_data.paint(
                painter,
                icon_rect,
                Qt.AlignmentFlag.AlignCenter,
                mode,
                QIcon.State.Off,
            )

        elif isinstance(item_data, QPixmap):
            icon_rect = option.rect.adjusted(padding, padding, -padding, -padding)
            fit_size = item_data.size().scaled(icon_rect.size(), Qt.AspectRatioMode.KeepAspectRatio)

            aligned_rect = QStyle.alignedRect(
                Qt.LayoutDirection.LeftToRight,
                Qt.AlignmentFlag.AlignCenter,
                fit_size,
                icon_rect,
            )

            painter.drawPixmap(aligned_rect, item_data)