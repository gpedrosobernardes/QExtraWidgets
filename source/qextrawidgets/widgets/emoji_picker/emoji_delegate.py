from PySide6.QtCore import QModelIndex, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem


class QLazyLoadingEmojiDelegate(QStyledItemDelegate):
    """A delegate for lazy loading emojis in a view.

    Signals:
        painted (QModelIndex): Emitted when an item is painted.
    """

    painted = Signal(QModelIndex)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """Paints the emoji item and emits the painted signal.

        Args:
            painter (QPainter): The painter to use.
            option (QStyleOptionViewItem): The style option.
            index (QModelIndex): The model index to paint.
        """
        self.painted.emit(index)
        super().paint(painter, option, index)
