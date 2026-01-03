from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPainter, QIcon
from PySide6.QtWidgets import QHeaderView, QStyle, QStyleOptionHeader


class CustomHeader(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)
        # Optional: Allows text to have "..." if it's too long
        self.setTextElideMode(Qt.TextElideMode.ElideRight)

    def paintSection(self, painter: QPainter, rect: QRect, logicalIndex):
        painter.save()

        # 1. Configure native style options
        opt = QStyleOptionHeader()
        self.initStyleOption(opt)
        opt.rect = rect
        opt.section = logicalIndex
        opt.textAlignment = Qt.AlignmentFlag.AlignCenter

        # Get data from model
        model = self.model()
        if model:
            # Text
            text = model.headerData(logicalIndex, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            opt.text = str(text) if text is not None else ""

            # Alignment
            alignment = model.headerData(logicalIndex, Qt.Orientation.Horizontal, Qt.ItemDataRole.TextAlignmentRole)
            if alignment:
                opt.textAlignment = alignment

            # Icon (Filter)
            icon = model.headerData(logicalIndex, Qt.Orientation.Horizontal, Qt.ItemDataRole.DecorationRole)

            # 2. Drawing Logic

            # Margin for the icon (if any)
            icon_size = 16  # Comfortable default size
            padding = 4

            # If there is an icon, reserve space on the right for it
            # so the native text doesn't draw over it
            if isinstance(icon, QIcon) and not icon.isNull():
                # Reduce the area where Qt can draw the text/background
                # to not cover our custom icon on the right
                # Note: Depending on the style, it might be better to draw the background first (control)
                # and then draw the icon and text manually if full control is desired.

                # Let's draw the native control (Background + Text)
                # But we'll trick the style saying there is no icon, as we'll draw it manually on the right
                opt.icon = QIcon()
                self.style().drawControl(QStyle.ControlElement.CE_Header, opt, painter, self)

                # Draw the icon aligned to the right manually
                icon_rect = QRect(
                    rect.right() - icon_size - padding,
                    rect.top() + (rect.height() - icon_size) // 2,
                    icon_size,
                    icon_size
                )

                # Icon state (active/disabled) based on header
                mode = QIcon.Mode.Normal
                if not self.isEnabled():
                    mode = QIcon.Mode.Disabled
                elif opt.state & QStyle.State_MouseOver:
                    mode = QIcon.Mode.Active

                icon.paint(painter, icon_rect, alignment=Qt.AlignmentFlag.AlignCenter, mode=mode)

            else:
                # Full standard native drawing
                self.style().drawControl(QStyle.ControlElement.CE_Header, opt, painter, self)

        painter.restore()
