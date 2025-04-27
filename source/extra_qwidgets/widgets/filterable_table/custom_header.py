from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPainter, QIcon
from PySide6.QtWidgets import QHeaderView


class CustomHeader(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)

    def paintSection(self, painter: QPainter, rect: QRect, logicalIndex):
        painter.save()
        painter.fillRect(rect, self.palette().button())
        pen = painter.pen()
        pen.setColor(self.palette().mid().color())
        painter.setPen(pen)
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        painter.restore()

        m = self.parent().model()
        text = m.headerData(logicalIndex, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
        alignment = m.headerData(logicalIndex, Qt.Orientation.Horizontal, Qt.ItemDataRole.TextAlignmentRole) or Qt.AlignmentFlag.AlignRight
        icon = m.headerData(logicalIndex, Qt.Orientation.Horizontal, Qt.ItemDataRole.DecorationRole)
        if not isinstance(icon, QIcon):
            icon = QIcon()

        icon_size = int(rect.height() * 0.8)

        painter.save()
        painter.setPen(self.palette().buttonText().color())
        text_rect = QRect(rect)
        text_rect.adjust(4, 0, -icon_size - 1, 0)  # 4px padding left, 1px padding right
        painter.drawText(text_rect, alignment | Qt.AlignmentFlag.AlignCenter, str(text))
        painter.restore()

        painter.save()
        x = rect.right() - icon_size
        y = rect.top() + (rect.height() - icon_size) // 2
        icon.paint(painter, QRect(x, y, icon_size, icon_size))
        painter.restore()