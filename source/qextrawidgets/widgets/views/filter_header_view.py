from PySide6.QtGui import QPalette
import typing
from PySide6.QtCore import QRect, Qt, Signal, QPoint, QEvent
from PySide6.QtGui import QPainter, QIcon, QMouseEvent
from PySide6.QtWidgets import (
    QHeaderView,
    QStyle,
    QStyleOptionHeader,
    QWidget,
    QApplication,
)


class QFilterHeaderView(QHeaderView):
    """A customized horizontal header for QFilterableTable that renders filter icons.

    This header overrides the default painting to draw a filter icon on the right
    side of the section if the model provides one via the DecorationRole.
    """

    filterClicked = Signal(int)

    def __init__(
        self, orientation: Qt.Orientation, parent: typing.Optional[QWidget] = None
    ) -> None:
        """Initializes the filter header.

        Args:
            orientation (Qt.Orientation): Orientation of the header (Horizontal).
            parent (QHeaderView, optional): Parent widget. Defaults to None.
        """
        super().__init__(orientation, parent)
        self.setSectionsClickable(False)
        self.setMouseTracking(True)
        self.setTextElideMode(Qt.TextElideMode.ElideRight)
        self._press_pos: typing.Optional[QPoint] = None
        self._current_hover_pos: typing.Optional[QPoint] = None

    def _get_icon_rect(self, section_rect: QRect) -> QRect:
        """Calculates the filter icon rectangle within the section."""
        icon_size = 16  # Comfortable default size
        padding = 4

        return QRect(
            section_rect.right() - icon_size - padding,
            section_rect.top() + (section_rect.height() - icon_size) // 2,
            icon_size,
            icon_size,
        )

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        """Updates hover position and triggers repaint."""
        self._current_hover_pos = e.pos()
        # We could optimize by only updating the affected section, but updating viewport is safer/easier
        self.viewport().update()
        super().mouseMoveEvent(e)

    def leaveEvent(self, e: QEvent) -> None:
        """Resets hover position when mouse leaves the header."""
        self._current_hover_pos = None
        self.viewport().update()
        super().leaveEvent(e)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        """Stores the position of the click to detect drags."""
        self._press_pos = e.pos()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        """Handles mouse release to manually trigger click signals."""
        super().mouseReleaseEvent(e)

        if self._press_pos is None:
            return

        # Check if it was a click (not a drag)
        moved = (
            e.pos() - self._press_pos
        ).manhattanLength() > QApplication.startDragDistance()
        if moved:
            return

        index = self.logicalIndexAt(e.pos())
        if index == -1:
            return

        # Only handle left clicks
        if e.button() == Qt.MouseButton.LeftButton:
            # 1. Reconstruct section geometry to check hit on icon
            # Logic borrowed from how paintSection gets the rect, but here we need valid geometry
            # sectionViewportPosition gives the start X relative to viewport
            x = self.sectionViewportPosition(index)
            w = self.sectionSize(index)
            h = self.height()
            section_rect = QRect(x, 0, w, h)

            icon_rect = self._get_icon_rect(section_rect)

            # 2. Check Hit
            if icon_rect.contains(e.pos()):
                # Clicked on filter icon -> Show Popup
                self.filterClicked.emit(index)
            else:
                # Clicked elsewhere -> Select Column
                # (Standard Behavior simulation, no modifiers needed anymore)
                self.sectionClicked.emit(index)

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
            text = model.headerData(
                logical_index, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole
            )
            if text is None:
                text = ""
            setattr(opt, "text", text)

            # Alignment
            alignment = model.headerData(
                logical_index,
                Qt.Orientation.Horizontal,
                Qt.ItemDataRole.TextAlignmentRole,
            )
            if alignment:
                setattr(opt, "textAlignment", alignment)

            # Icon (Filter)
            icon = model.headerData(
                logical_index, Qt.Orientation.Horizontal, Qt.ItemDataRole.DecorationRole
            )

            # 2. Drawing Logic
            icon_size = 16  # Comfortable default size
            padding = 4

            # If there is an icon, reserve space on the right for it
            if isinstance(icon, QIcon) and not icon.isNull():
                # Draw the native control (Background + Text)
                # We'll trick the style saying there is no icon, as we'll draw it manually on the right
                setattr(opt, "icon", QIcon())
                self.style().drawControl(
                    QStyle.ControlElement.CE_Header, opt, painter, self
                )

                # Draw the icon aligned to the right manually
                icon_rect = self._get_icon_rect(rect)

                # Icon state (active/disabled) based on header
                mode = QIcon.Mode.Normal
                if not self.isEnabled():
                    mode = QIcon.Mode.Disabled
                else:
                    # Check if mouse is hovering THIS icon
                    if self._current_hover_pos and icon_rect.contains(
                        self._current_hover_pos
                    ):
                        # Draw hover background
                        palette = typing.cast(QPalette, opt.palette)
                        hover_color = palette.text().color()
                        hover_color.setAlphaF(0.1)
                        painter.setPen(Qt.PenStyle.NoPen)
                        painter.setBrush(hover_color)
                        # Adjust rect slightly to give some padding
                        painter.drawRoundedRect(icon_rect.adjusted(-2, -2, 2, 2), 2, 2)

                        # mode remains Normal
                    elif (
                        typing.cast(QStyle.StateFlag, opt.state)
                        & QStyle.StateFlag.State_MouseOver
                    ):
                        # Fallback: if section is hovered but not icon, maybe different state?
                        # For now, keep Normal unless specifically hovering icon, OR use Active if just section is hovered?
                        # User requested "hover effect on the icon", usually implies specific icon hover.
                        pass

                icon.paint(
                    painter,
                    icon_rect,
                    alignment=Qt.AlignmentFlag.AlignCenter,
                    mode=mode,
                )

            else:
                # Full standard native drawing
                self.style().drawControl(
                    QStyle.ControlElement.CE_Header, opt, painter, self
                )

        painter.restore()
