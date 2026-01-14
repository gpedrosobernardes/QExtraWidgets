from PySide6.QtCore import QModelIndex, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem


class QLazyLoadingEmojiDelegate(QStyledItemDelegate):
    painted = Signal(QModelIndex)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        self.painted.emit(index)
        super().paint(painter, option, index)
