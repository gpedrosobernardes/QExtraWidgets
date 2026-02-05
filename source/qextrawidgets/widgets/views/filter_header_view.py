import typing
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPainter, QIcon
from PySide6.QtWidgets import QHeaderView, QStyle, QStyleOptionHeader, QWidget


class QFilterHeaderView(QHeaderView):
    """A customized horizontal header for QFilterableTable that renders filter icons.

    This header overrides the default painting to draw a filter icon on the right
    side of the section if the model provides one via the DecorationRole.
    """

    def __init__(self, orientation: Qt.Orientation, parent: typing.Optional[QWidget] = None) -> None:
        """Initializes the filter header.

        Args:
            orientation (Qt.Orientation): Orientation of the header (Horizontal).
            parent (QHeaderView, optional): Parent widget. Defaults to None.
        """
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)
        self.setTextElideMode(Qt.TextElideMode.ElideRight)

    def paintSection(self, painter: QPainter, rect: QRect, logical_index: int) -> None:
        """Paints the header section with an optional filter icon.

        Args:
            painter (QPainter): The painter to use.
            rect (QRect): The rectangle to paint in.
            logical_index (int): The logical index of the section.
        """
        painter.save()

        # 1. Configure native style options
        opt = QStyleOptionHeader()
        self.initStyleOption(opt)

        setattr(opt, "rect", rect)
        setattr(opt, "section", logical_index)
        setattr(opt, "textAlignment", Qt.AlignmentFlag.AlignCenter)

        # Get data from model
        model = self.model()
        if model:
            # Text
            text = model.headerData(logical_index, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            if text is None:
                text = ""
            setattr(opt, "text", text)

            # Alignment
            alignment = model.headerData(logical_index, Qt.Orientation.Horizontal, Qt.ItemDataRole.TextAlignmentRole)
            if alignment:
                setattr(opt, "textAlignment", alignment)

            # Icon (Filter)
            icon = model.headerData(logical_index, Qt.Orientation.Horizontal, Qt.ItemDataRole.DecorationRole)

            # 2. Drawing Logic
            icon_size = 16  # Comfortable default size
            padding = 4

            # If there is an icon, reserve space on the right for it
            if isinstance(icon, QIcon) and not icon.isNull():
                # Draw the native control (Background + Text)
                # We'll trick the style saying there is no icon, as we'll draw it manually on the right
                setattr(opt, "icon", QIcon())
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
                elif typing.cast(QStyle.StateFlag, opt.state) & QStyle.StateFlag.State_MouseOver:
                    mode = QIcon.Mode.Active

                icon.paint(painter, icon_rect, alignment=Qt.AlignmentFlag.AlignCenter, mode=mode)

            else:
                # Full standard native drawing
                self.style().drawControl(QStyle.ControlElement.CE_Header, opt, painter, self)

        painter.restore()
