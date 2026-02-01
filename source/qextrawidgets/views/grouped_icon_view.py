from PySide6.QtCore import (
    QModelIndex,
    QSize,
    Qt,
    QRect,
    QPoint,
    QEvent,
    Signal  # [CHANGED] Added Signal import
)
from PySide6.QtGui import QCursor, QPainter, QMouseEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QStyleOptionViewItem,
    QStyle,
    QWidget
)
from typing import Optional, Any

from qextrawidgets.delegates.grouped_icon_delegate import QGroupedIconDelegate


class QGroupedIconView(QAbstractItemView):
    """
    A custom item view that displays categories as headers (accordion style)
    and children items in a grid layout using icons.

    Attributes:
        itemEntered (Signal): Emitted when the mouse enters an item (QModelIndex).
        itemExited (Signal): Emitted when the mouse leaves an item (QModelIndex).
        _item_rects (dict): Cache of visual rectangles for indices.
        _expanded_rows (set): Set of row numbers (categories) that are currently expanded.
        _hover_index (QModelIndex): The index currently under the mouse cursor.
        _margin (int): Margin between items.
        _header_height (int): Height of the category headers.
    """

    # [CHANGED] Signal Definitions
    itemEntered = Signal(QModelIndex)
    itemExited = Signal(QModelIndex)

    def __init__(
            self,
            parent: Optional[QWidget] = None,
            icon_size: QSize = QSize(100, 100),
            margin: int = 8,
            header_height: int = 36
    ):
        """
        Initializes the AccordionGridView with configurable layout parameters.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
            icon_size (QSize, optional): The fixed size for grid items. Defaults to 100x100.
            margin (int, optional): The margin between items in pixels. Defaults to 8.
            header_height (int, optional): The height of category headers in pixels. Defaults to 36.
        """
        super().__init__(parent)

        self._item_rects: dict[QModelIndex, QRect] = {}

        # View State
        self._expanded_rows: set[int] = set()
        self._hover_index: QModelIndex = QModelIndex()

        # Layout Configuration
        self._margin: int = margin
        self._header_height: int = header_height

        # Use standard QAbstractItemView property for item size
        self.setIconSize(icon_size)

        # Mouse Tracking & Attributes
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Connect Signals
        self.verticalScrollBar().valueChanged.connect(self._on_scroll_value_changed)

        # Set Delegate
        self.setItemDelegate(QGroupedIconDelegate(self, arrow_icon=None))

    # -------------------------------------------------------------------------
    # Public API (Getters & Setters)
    # -------------------------------------------------------------------------

    def setIconSize(self, size: QSize) -> None:
        """
        Sets the size of the grid items. Overrides QAbstractItemView.setIconSize
        to ensure layout update.
        """
        super().setIconSize(size)
        self.updateGeometries()
        self.viewport().update()

    def setMargin(self, margin: int) -> None:
        """
        Sets the margin/spacing between items and headers.

        Args:
            margin (int): The margin in pixels.
        """
        if self._margin == margin:
            return
        self._margin = margin
        self.updateGeometries()
        self.viewport().update()

    def margin(self) -> int:
        """
        Returns the current margin.

        Returns:
            int: The margin in pixels.
        """
        return self._margin

    def setHeaderHeight(self, height: int) -> None:
        """
        Sets the height of the category headers.

        Args:
            height (int): The height in pixels.
        """
        if self._header_height == height:
            return
        self._header_height = height
        self.updateGeometries()
        self.viewport().update()

    def headerHeight(self) -> int:
        """
        Returns the current header height.

        Returns:
            int: The header height in pixels.
        """
        return self._header_height

    def isRowExpanded(self, row: int) -> bool:
        """
        Checks if a specific category row is expanded.
        Used by the Delegate to draw the expansion arrow.

        Args:
            row (int): The row index of the category.

        Returns:
            bool: True if expanded, False otherwise.
        """
        return row in self._expanded_rows

    # -------------------------------------------------------------------------
    # Internal Logic Helpers
    # -------------------------------------------------------------------------

    def _is_category(self, index: QModelIndex) -> bool:
        """Determines if the index represents a category (root level)."""
        return index.isValid() and not index.parent().isValid()

    def _is_item(self, index: QModelIndex) -> bool:
        """Determines if the index represents an item (child of root)."""
        return index.isValid() and index.parent().isValid()

    def _on_scroll_value_changed(self, value: int) -> None:
        """Handle scroll bar changes to update hover state."""
        self._recalculate_hover()
        self.viewport().update()

    def _recalculate_hover(self) -> None:
        """Updates the internal hover index based on global cursor position."""
        pos_global = QCursor.pos()
        pos_local = self.viewport().mapFromGlobal(pos_global)

        if self.viewport().rect().contains(pos_local):
            new_index = self.indexAt(pos_local)
        else:
            new_index = QModelIndex()

        # [CHANGED] Signal emission logic
        if new_index != self._hover_index:
            # Emit exited for the previous valid item
            if self._hover_index.isValid():
                self.itemExited.emit(self._hover_index)

            self._hover_index = new_index

            # Emit entered for the new valid item
            if self._hover_index.isValid():
                self.itemEntered.emit(self._hover_index)

            if not self.verticalScrollBar().isSliderDown():
                self.viewport().update()

    # -------------------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        index = self.indexAt(event.position().toPoint())

        if index.isValid():
            # If clicked on a Category (Header)
            if self._is_category(index):
                row = index.row()

                # Toggle local state
                if row in self._expanded_rows:
                    self._expanded_rows.remove(row)
                else:
                    self._expanded_rows.add(row)

                # Force layout recalculation and repaint
                self.updateGeometries()
                self.viewport().update()

                # Accept event to prevent default selection propagation
                event.accept()
                return

            # If clicked on an Item
            elif self._is_item(index):
                # Use default behavior (select the item)
                super().mousePressEvent(event)
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._recalculate_hover()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        # [CHANGED] Emit exit signal when mouse leaves the widget entirely
        if self._hover_index.isValid():
            self.itemExited.emit(self._hover_index)

        self._hover_index = QModelIndex()
        self.viewport().update()
        super().leaveEvent(event)

    def paintEvent(self, event: QEvent) -> None:
        painter = QPainter(self.viewport())
        region = event.rect()
        scroll_y = self.verticalScrollBar().value()

        option = QStyleOptionViewItem()
        option.initFrom(self)

        for index, rect in self._item_rects.items():
            visual_rect = rect.translated(0, -scroll_y)

            # Optimization: Skip painting if outside dirty region
            if not visual_rect.intersects(region):
                continue

            option.rect = visual_rect
            option.state = QStyle.State.State_None

            if self.isEnabled():
                option.state |= QStyle.State.State_Enabled
            if self.selectionModel().isSelected(index):
                option.state |= QStyle.State.State_Selected
            if index == self._hover_index:
                option.state |= QStyle.State.State_MouseOver

            self.itemDelegate(index).paint(painter, option, index)

    # -------------------------------------------------------------------------
    # QAbstractItemView Implementation
    # -------------------------------------------------------------------------

    def updateGeometries(self) -> None:
        if not self.model():
            return

        self._item_rects.clear()
        width = self.viewport().width()
        x = 0
        y = 0

        # Use standard iconSize()
        item_w = self.iconSize().width()
        item_h = self.iconSize().height()

        effective_width = width - (2 * self._margin)
        # Calculate columns available
        cols = max(1, effective_width // (item_w + self._margin))
        root = self.rootIndex()

        # Iterate only over Root (Categories)
        for r in range(self.model().rowCount(root)):
            cat_index = self.model().index(r, 0, root)

            # 1. Define Category Rectangle
            self._item_rects[cat_index] = QRect(0, y, width, self._header_height)
            y += self._header_height

            # 2. If expanded in VIEW, calculate children positions
            if r in self._expanded_rows:
                child_count = self.model().rowCount(cat_index)
                if child_count > 0:
                    y += self._margin
                    col_current = 0

                    for c_row in range(child_count):
                        child = self.model().index(c_row, 0, cat_index)

                        # Grid Positioning
                        px = self._margin + (col_current * (item_w + self._margin))
                        self._item_rects[child] = QRect(px, y, item_w, item_h)

                        col_current += 1
                        if col_current >= cols:
                            col_current = 0
                            y += item_h + self._margin

                    # Add bottom margin if the last row wasn't completed
                    if col_current != 0:
                        y += item_h + self._margin

        content_height = y
        scroll_range = max(0, content_height - self.viewport().height())

        self.verticalScrollBar().setRange(0, scroll_range)
        self.verticalScrollBar().setPageStep(self.viewport().height())
        self.verticalScrollBar().setSingleStep(self._header_height)

        super().updateGeometries()

    def visualRect(self, index: QModelIndex) -> QRect:
        rect = self._item_rects.get(index)
        if rect:
            return rect.translated(0, -self.verticalScrollBar().value())
        return QRect()

    def indexAt(self, point: QPoint) -> QModelIndex:
        real_point = point + QPoint(0, self.verticalScrollBar().value())
        for index, rect in self._item_rects.items():
            if rect.contains(real_point):
                return index
        return QModelIndex()

    def scrollTo(self, index: QModelIndex, hint=QAbstractItemView.ScrollHint.EnsureVisible) -> None:
        rect = self._item_rects.get(index)
        if rect:
            self.verticalScrollBar().setValue(rect.y())

    # -------------------------------------------------------------------------
    # Abstract Stubs
    # -------------------------------------------------------------------------

    def horizontalOffset(self) -> int:
        return 0

    def verticalOffset(self) -> int:
        return self.verticalScrollBar().value()

    def moveCursor(self, cursor_action, modifiers) -> QModelIndex:
        return QModelIndex()

    def setSelection(self, rect: QRect, command) -> None:
        pass

    def visualRegionForSelection(self, selection) -> QRect:
        return self.viewport().rect()