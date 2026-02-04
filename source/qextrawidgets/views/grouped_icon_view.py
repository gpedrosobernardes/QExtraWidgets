import typing
from PySide6.QtCore import (
    QModelIndex,
    QPersistentModelIndex,
    QSize,
    Qt,
    QRect,
    QPoint,
    QEvent,
    Signal,
    QAbstractItemModel,
    QTimer,
    QItemSelection
)
from PySide6.QtGui import QCursor, QPainter, QMouseEvent, QRegion, QPaintEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QStyleOptionViewItem,
    QStyle,
    QWidget
)
from typing import Optional

from qextrawidgets.delegates.grouped_icon_delegate import QGroupedIconDelegate
from qextrawidgets.items.emoji_category_item import QEmojiCategoryItem


class QGroupedIconView(QAbstractItemView):
    """
    A custom item view that displays categories as headers (accordion style)
    and children items in a grid layout using icons.

    Uses QPersistentModelIndex for internal caching and QTimer for layout debouncing.
    The expansion state is stored in the model using ExpansionStateRole.
    """

    itemEntered = Signal(QModelIndex)
    itemExited = Signal(QModelIndex)
    itemClicked = Signal(QModelIndex)

    def __init__(
            self,
            parent: Optional[QWidget] = None,
            icon_size: QSize = QSize(100, 100),
            margin: int = 8,
            header_height: int = 36
    ):
        """
        Initialize the QGroupedIconView.

        Args:
            parent (Optional[QWidget]): The parent widget.
            icon_size (QSize): The size of the icons in the grid. Defaults to 100x100.
            margin (int): The margin between items and headers. Defaults to 8.
            header_height (int): The height of the category headers. Defaults to 36.
        """
        super().__init__(parent)

        # Cache using Persistent Indices
        self._item_rects: dict[QPersistentModelIndex, QRect] = {}

        # Debounce Timer for Layout Updates
        self._layout_timer = QTimer(self)
        self._layout_timer.setSingleShot(True)
        self._layout_timer.setInterval(0)
        self._layout_timer.timeout.connect(self._execute_delayed_layout)

        # View State
        self._hover_index: QPersistentModelIndex = QPersistentModelIndex()
        self._expanded_items: set[QPersistentModelIndex] = set()

        # Layout Configuration
        self._margin: int = margin
        self._header_height: int = header_height

        self.setIconSize(icon_size)

        # Mouse Tracking
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Disable default AutoScroll to prevent unintentional scrolling on click-drag
        self.setAutoScroll(False)

        # Connect Scroll Signals
        self.verticalScrollBar().valueChanged.connect(self._on_scroll_value_changed)

        # Set Delegate
        self.setItemDelegate(QGroupedIconDelegate(self, arrow_icon=None))

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def itemDelegate(self, _: typing.Union[QModelIndex, QPersistentModelIndex, None] = None) -> QGroupedIconDelegate:
        """Returns the item delegate used by the view."""
        return typing.cast(QGroupedIconDelegate, super().itemDelegate())

    def setIconSize(self, size: QSize) -> None:
        """
        Set the size of the icons in the grid view.

        Args:
            size (QSize): The new size for the icons.
        """
        super().setIconSize(size)
        self._schedule_layout()

    def setMargin(self, margin: int) -> None:
        """
        Set the margin between items and headers.

        Args:
            margin (int): The new margin value in pixels.
        """
        if self._margin == margin:
            return
        self._margin = margin
        self._schedule_layout()

    def margin(self) -> int:
        """
        Get the current margin between items and headers.

        Returns:
            int: The current margin in pixels.
        """
        return self._margin

    def setHeaderHeight(self, height: int) -> None:
        """
        Set the height of the category headers.

        Args:
            height (int): The new header height in pixels.
        """
        if self._header_height == height:
            return
        self._header_height = height
        self._schedule_layout()

    def headerHeight(self) -> int:
        """
        Get the current height of the category headers.

        Returns:
            int: The header height in pixels.
        """
        return self._header_height

    def isExpanded(self, index: QModelIndex) -> bool:
        """Return True if the category at index is expanded."""
        if not index.isValid():
            return False
        return QPersistentModelIndex(index) in self._expanded_items

    def setExpanded(self, index: QModelIndex, expanded: bool) -> None:
        """Set the expansion state of the category at index."""
        if not index.isValid():
            return

        p_index = QPersistentModelIndex(index)
        if expanded:
            self._expanded_items.add(p_index)
        else:
            self._expanded_items.discard(p_index)
        
        self._schedule_layout()

    def expandAll(self) -> None:
        """Expand all categories."""
        if not self.model():
            return
        
        count = self.model().rowCount()
        for i in range(count):
            index = self.model().index(i, 0)
            self._expanded_items.add(QPersistentModelIndex(index))
        self._schedule_layout()

    def collapseAll(self) -> None:
        """Collapse all categories."""
        self._expanded_items.clear()
        self._schedule_layout()

    # -------------------------------------------------------------------------
    # Internal Logic Helpers
    # -------------------------------------------------------------------------

    def _is_category(self, index: typing.Union[QModelIndex, QPersistentModelIndex]) -> bool:
        """Check if the given index represents a category (header)."""
        return index.isValid() and not index.parent().isValid()

    def _is_item(self, index: typing.Union[QModelIndex, QPersistentModelIndex]) -> bool:
        """Check if the given index represents a child item."""
        return index.isValid() and index.parent().isValid()

    def _persistent_to_index(self, persistent: QPersistentModelIndex) -> QModelIndex:
        """Helper to convert QPersistentModelIndex to QModelIndex (workaround for PySide6)."""
        if not persistent.isValid():
            return QModelIndex()
        model = persistent.model()
        if not model:
            return QModelIndex()
        return model.index(persistent.row(), persistent.column(), persistent.parent())

    def _on_scroll_value_changed(self, value: int) -> None:
        self._recalculate_hover()
        self.viewport().update()

    def _recalculate_hover(self) -> None:
        if not self._item_rects:
            return

        pos_global = QCursor.pos()
        pos_local = self.viewport().mapFromGlobal(pos_global)

        if self.viewport().rect().contains(pos_local):
            new_index_temp = self.indexAt(pos_local)
        else:
            new_index_temp = QModelIndex()

        new_persistent = QPersistentModelIndex(new_index_temp)

        if new_persistent != self._hover_index:
            if self._hover_index.isValid():
                self.itemExited.emit(self._persistent_to_index(self._hover_index))

            self._hover_index = new_persistent

            if self._hover_index.isValid():
                self.itemEntered.emit(self._persistent_to_index(self._hover_index))

            if not self.verticalScrollBar().isSliderDown():
                self.viewport().update()

    # -------------------------------------------------------------------------
    # Layout Scheduling & Cache Management
    # -------------------------------------------------------------------------

    def _schedule_layout(self) -> None:
        if not self._layout_timer.isActive():
            self._layout_timer.start()

    def _execute_delayed_layout(self) -> None:
        self.updateGeometries()
        self.viewport().update()

    def _clear_cache(self, *args) -> None:
        self._item_rects.clear()
        self._hover_index = QPersistentModelIndex()
        # Clean up invalid persistent indices from expansion set
        self._expanded_items = {pi for pi in self._expanded_items if pi.isValid()}
        self.viewport().update()

    def setModel(self, model: Optional[QAbstractItemModel]) -> None:
        """
        Set the model for the view.

        Connects to necessary signals for handling layout updates and structural changes.

        Args:
            model (Optional[QAbstractItemModel]): The model to be set.
        """
        current_model = self.model()
        if current_model == model:
            return

        if current_model:
            try:
                current_model.layoutChanged.disconnect(self._on_layout_changed)
                current_model.modelReset.disconnect(self._on_model_reset)
                current_model.rowsInserted.disconnect(self._on_rows_inserted)
                current_model.rowsRemoved.disconnect(self._on_rows_removed)
                current_model.dataChanged.disconnect(self._on_data_changed)

                current_model.layoutAboutToBeChanged.disconnect(self._clear_cache)
                current_model.rowsAboutToBeRemoved.disconnect(self._clear_cache)
            except Exception:
                pass

        super().setModel(model)
        self._expanded_items.clear()

        if model:
            model.layoutAboutToBeChanged.connect(self._clear_cache)
            model.rowsAboutToBeRemoved.connect(self._clear_cache)

            model.layoutChanged.connect(self._on_layout_changed)
            model.modelReset.connect(self._on_model_reset)
            model.rowsInserted.connect(self._on_rows_inserted)
            model.rowsRemoved.connect(self._on_rows_removed)
            model.dataChanged.connect(self._on_data_changed)

    def _on_layout_changed(self, *args, **kwargs) -> None:
        self._schedule_layout()

    def _on_model_reset(self) -> None:
        self._expanded_items.clear()
        self._schedule_layout()

    def _on_rows_inserted(self, parent, start, end):
        self._schedule_layout()

    def _on_rows_removed(self, parent, start, end):
        self._schedule_layout()

    def _on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: Optional[list[int]] = None) -> None:
        if roles is None:
            roles = []
        
        # NOTE: ExpansionStateRole check removed as it is now internal state
        
        # [CRUCIAL] Se for uma mudança de dados (como o ícone chegando), força a repintura!
        if not roles or Qt.ItemDataRole.DecorationRole in roles:
            self.update(top_left)


    # -------------------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse press events.

        Toggles category expansion or emits itemClicked signal.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if not self._item_rects: return

        index = self.indexAt(event.position().toPoint())

        if index.isValid() and event.button() == Qt.MouseButton.LeftButton:
            if self._is_category(index):
                self.setExpanded(index, not self.isExpanded(index))
                event.accept()
                return
            elif self._is_item(index):
                self.itemClicked.emit(index)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse move events to track hover state.

        Args:
            event (QMouseEvent): The mouse event.
        """
        self._recalculate_hover()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """
        Handle mouse leave events to reset hover state.

        Args:
            event (QEvent): The leave event.
        """
        if self._hover_index.isValid():
            self.itemExited.emit(self._persistent_to_index(self._hover_index))
        self._hover_index = QPersistentModelIndex()
        self.viewport().update()
        super().leaveEvent(event)

    # noinspection PyUnresolvedReferences
    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paint the items in the view.

        Args:
            event (QPaintEvent): The paint event.
        """
        if not self._item_rects:
            return

        painter = QPainter(self.viewport())
        region = event.region()
        scroll_y = self.verticalScrollBar().value()

        option: typing.Any = QStyleOptionViewItem()
        option.initFrom(self)

        for p_index, rect in self._item_rects.items():
            if not p_index.isValid():
                continue

            index = self._persistent_to_index(p_index)
            if not index.isValid():
                continue

            visual_rect = rect.translated(0, -scroll_y)

            if not visual_rect.intersects(region.boundingRect()):
                continue

            option.rect = visual_rect
            option.state = QStyle.StateFlag.State_None

            if self.isEnabled():
                option.state |= QStyle.StateFlag.State_Enabled
            if self.selectionModel().isSelected(index):
                option.state |= QStyle.StateFlag.State_Selected

            if p_index == self._hover_index:
                option.state |= QStyle.StateFlag.State_MouseOver

            if self.isExpanded(index):
                option.state |= QStyle.StateFlag.State_Open

            self.itemDelegate(index).paint(painter, option, index)

    # -------------------------------------------------------------------------
    # QAbstractItemView Implementation
    # -------------------------------------------------------------------------

    def updateGeometries(self) -> None:
        """
        Recalculate the layout of item rectangles and update scrollbars.
        """
        if not self.model():
            return

        self._item_rects.clear()
        width = self.viewport().width()
        y = 0

        item_w = self.iconSize().width()
        item_h = self.iconSize().height()

        effective_width = width - (2 * self._margin)
        cols = max(1, effective_width // (item_w + self._margin))
        root = self.rootIndex()

        row_count = self.model().rowCount(root)

        for r in range(row_count):
            cat_index = self.model().index(r, 0, root)
            if not cat_index.isValid():
                continue

            is_expanded = self.isExpanded(cat_index)

            self._item_rects[QPersistentModelIndex(cat_index)] = QRect(0, y, width, self._header_height)
            y += self._header_height

            if is_expanded:
                child_count = self.model().rowCount(cat_index)
                if child_count > 0:
                    y += self._margin
                    col_current = 0

                    for c_row in range(child_count):
                        child = self.model().index(c_row, 0, cat_index)
                        if not child.isValid():
                            continue

                        px = self._margin + (col_current * (item_w + self._margin))
                        self._item_rects[QPersistentModelIndex(child)] = QRect(px, y, item_w, item_h)

                        col_current += 1
                        if col_current >= cols:
                            col_current = 0
                            y += item_h + self._margin

                    if col_current != 0:
                        y += item_h + self._margin

        content_height = y
        scroll_range = max(0, content_height - self.viewport().height())

        self.verticalScrollBar().setRange(0, scroll_range)
        self.verticalScrollBar().setPageStep(self.viewport().height())
        self.verticalScrollBar().setSingleStep(self._header_height)

        super().updateGeometries()

    def visualRect(self, index: typing.Union[QModelIndex, QPersistentModelIndex]) -> QRect:
        """
        Return the rectangle on the viewport occupied by the item at index.

        Args:
            index (QModelIndex | QPersistentModelIndex): The index of the item.

        Returns:
            QRect: The visual rectangle.
        """
        p_index = QPersistentModelIndex(index)
        rect = self._item_rects.get(p_index)
        if rect:
            return rect.translated(0, -self.verticalScrollBar().value())
        return QRect()

    def indexAt(self, point: QPoint) -> QModelIndex:
        """
        Return the model index of the item at the viewport coordinates point.

        Args:
            point (QPoint): The coordinates in the viewport.

        Returns:
            QModelIndex: The index at the given point, or valid if not found.
        """
        if not self._item_rects:
            return QModelIndex()

        real_point = point + QPoint(0, self.verticalScrollBar().value())
        for p_index, rect in self._item_rects.items():
            if rect.contains(real_point):
                return self._persistent_to_index(p_index)
        return QModelIndex()

    def scrollTo(self, index: typing.Union[QModelIndex, QPersistentModelIndex], hint: QAbstractItemView.ScrollHint = QAbstractItemView.ScrollHint.EnsureVisible) -> None:
        """
        Scroll the view to ensure the item at index is visible.

        Args:
            index (QModelIndex | QPersistentModelIndex): The index to scroll to.
            hint (QAbstractItemView.ScrollHint): The scroll hint.
        """
        p_index = QPersistentModelIndex(index)
        rect = self._item_rects.get(p_index)
        if not rect:
            return

        # [CHANGED] Hybrid Behavior:
        # 1. Categories: Always force scroll to top (Classic Behavior).
        if self._is_category(index):
            self.verticalScrollBar().setValue(rect.y())
            return

        # 2. Items: Smart scroll (New Behavior) - Only scroll if needed.
        scroll_val = self.verticalScrollBar().value()
        viewport_height = self.viewport().height()

        item_top = rect.y()
        item_bottom = rect.bottom()

        if hint == QAbstractItemView.ScrollHint.EnsureVisible:
            if item_top < scroll_val:
                self.verticalScrollBar().setValue(item_top)
            elif item_bottom > scroll_val + viewport_height:
                self.verticalScrollBar().setValue(item_bottom - viewport_height)

        elif hint == QAbstractItemView.ScrollHint.PositionAtTop:
            self.verticalScrollBar().setValue(item_top)

        elif hint == QAbstractItemView.ScrollHint.PositionAtBottom:
            self.verticalScrollBar().setValue(item_bottom - viewport_height)

        elif hint == QAbstractItemView.ScrollHint.PositionAtCenter:
            center_target = int(item_top - (viewport_height / 2) + (rect.height() / 2))
            self.verticalScrollBar().setValue(center_target)

    # -------------------------------------------------------------------------
    # Abstract Stubs
    # -------------------------------------------------------------------------

    def horizontalOffset(self) -> int:
        """Return the horizontal offset of the view (always 0 for this view)."""
        return 0

    def verticalOffset(self) -> int:
        """Return the vertical offset of the view."""
        return self.verticalScrollBar().value()

    def moveCursor(self, cursor_action, modifiers) -> QModelIndex:
        """
        Move the cursor in response to key navigation (Not implemented).

        Returns:
            QModelIndex: An invalid index.
        """
        return QModelIndex()

    def setSelection(self, rect: QRect, command) -> None:
        """Apply selection to items within the rectangle (Not implemented)."""
        pass

    def visualRegionForSelection(self, selection: QItemSelection) -> QRegion:
        """
        Return the region covered by the selection (Not implemented).

        Returns:
            QRegion: The total viewport rect as a placeholder.
        """
        return QRegion(self.viewport().rect())