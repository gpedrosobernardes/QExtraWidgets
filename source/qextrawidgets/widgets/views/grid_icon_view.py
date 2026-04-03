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
    QItemSelection,
    QItemSelectionModel,
    Slot,
)
from PySide6.QtGui import QCursor, QPainter, QMouseEvent, QRegion, QPaintEvent
from PySide6.QtWidgets import QAbstractItemView, QStyleOptionViewItem, QStyle, QWidget

from qextrawidgets.widgets.delegates.grid_icon_delegate import QGridIconDelegate
import logging
import time

class QGridIconView(QAbstractItemView):
    """
    A custom item view that displays items in a grid layout.

    Uses QPersistentModelIndex for internal caching and QTimer for layout debouncing.
    """

    itemEntered = Signal(QModelIndex)
    itemExited = Signal(QModelIndex)
    itemClicked = Signal(QModelIndex)

    def __init__(
        self,
        parent: typing.Optional[QWidget] = None,
        icon_size: QSize = QSize(100, 100),
        margin: int = 8,
    ):
        """
        Initialize the QGridIconView.

        Args:
            parent (Optional[QWidget]): The parent widget.
            icon_size (QSize): The size of the icons in the grid. Defaults to 100x100.
            margin (int): The margin between items. Defaults to 8.
        """
        super().__init__(parent)

        # Cache using Persistent Indices
        self._item_rects: dict[QPersistentModelIndex, QRect] = {}
        self._item_indexes: dict[int, dict[int, typing.Tuple[QPersistentModelIndex, QRect]]] = {}

        self._hidden_rows: typing.List[int] = []

        # Debounce Timer for Layout Updates
        self._layout_timer = QTimer(self)
        self._layout_timer.setSingleShot(True)
        self._layout_timer.setInterval(0)
        self._layout_timer.timeout.connect(self._execute_delayed_layout)

        # View State
        self._hover_index: QPersistentModelIndex = QPersistentModelIndex()

        # Layout Configuration
        self._margin: int = margin

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

        # Set Delegate (can be overridden)
        self.setItemDelegate(QGridIconDelegate(self))

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def itemDelegate(
        self, _: typing.Union[QModelIndex, QPersistentModelIndex, None] = None
    ) -> QGridIconDelegate:
        """Returns the item delegate used by the view."""
        return typing.cast(QGridIconDelegate, super().itemDelegate())

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
        Set the margin between items.

        Args:
            margin (int): The new margin value in pixels.
        """
        if self._margin == margin:
            return
        self._margin = margin
        self._schedule_layout()

    def margin(self) -> int:
        """
        Get the current margin between items.

        Returns:
            int: The current margin in pixels.
        """
        return self._margin

    def setRowHidden(self, row: int, hidden: bool) -> None:
        """
        Hide/show the row from the user view.

        Args:
            row (int): The row to hide/show.
            hidden (bool): Whether the row should be hidden.
        """
        if hidden:
            if not self.isRowHidden(row):
                self._hidden_rows.append(row)
        else:
            if self.isRowHidden(row):
                self._hidden_rows.remove(row)

        self._schedule_layout()

    def isRowHidden(self, row: int) -> bool:
        """
        Check if the given row is hidden.

        Args:
            row: Row index to check.

        Returns:
            If its hidden, return True.
        """
        return row in self._hidden_rows

    # -------------------------------------------------------------------------
    # Internal Logic Helpers
    # -------------------------------------------------------------------------

    @Slot()
    def _on_scroll_value_changed(self) -> None:
        """Handle the scroll value changing."""
        self._recalculate_hover()
        self.viewport().update()

    def _recalculate_hover(self) -> None:
        """Calculates the hover index and cache it in the class instance."""
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
                self.itemExited.emit(QPersistentModelIndex(self._hover_index))

            self._hover_index = new_persistent

            if self._hover_index.isValid():
                self.itemEntered.emit(QPersistentModelIndex(self._hover_index))

            if not self.verticalScrollBar().isSliderDown():
                self.viewport().update()

    def _init_option(self, option: QStyleOptionViewItem, index: QPersistentModelIndex, visual_rect: QRect) -> None:
        """
        Initialize the style option for the given index.

        Args:
            option (QStyleOptionViewItem): The option to initialize.
            index (QModelIndex): The index of the item.
        """
        # Optimization: We check intersections in paintEvent loop usually,
        # but here we just set the rect. The caller (paintEvent) already checks visibility.
        setattr(option, "rect", visual_rect)

        state = QStyle.StateFlag.State_None

        if self.isEnabled():
            state |= QStyle.StateFlag.State_Enabled

        if self.selectionModel().isSelected(index):
            state |= QStyle.StateFlag.State_Selected

        if index == self._hover_index:
            state |= QStyle.StateFlag.State_MouseOver

        setattr(option, "state", state)

    def _get_coordinates_at(self, point: QPoint) -> typing.Tuple[int, int]:
        """
        Translates a point into row and column coordinates.

        Args:
            point: QPoint instance.

        Returns:
            A Tuple of row and column.
        """
        logging.debug(f"Looking for index at {point}")
        item_w = self.iconSize().width()
        item_h = self.iconSize().height()

        col = point.x() // (item_w + self._margin)
        row = point.y() // (item_h + self._margin)
        return row, col

    def _rows(self, parent_index: QModelIndex) -> typing.Generator[QPersistentModelIndex]:
        """
        Generator of the row indices. Gets only valid and visible rows.

        Args:
            parent_index: Parent index of the rows.

        Returns:
            Generator of row indices.
        """

        row_count = self.model().rowCount(parent_index)
        for r in range(row_count):
            index = self.model().index(r, 0, parent_index)
            if index.isValid() and not self.isRowHidden(r):
                yield QPersistentModelIndex(index)

    def _visible_items(self) -> typing.Generator[typing.Tuple[QPersistentModelIndex, QRect]]:
        """
        Generator of the visible items. Calculates the first and last row visible to get directly what is visible.

        Returns:
            Generator of tuples of (QPersistentModelIndex, QRect).
        """
        viewport_rect = self.viewport().rect()
        viewport_rect.translate(QPoint(0, self.verticalScrollBar().value()))

        first_row, _ = self._get_coordinates_at(viewport_rect.topLeft())
        last_row, _ = self._get_coordinates_at(viewport_rect.bottomRight())

        for i in range(first_row, last_row + 1):
            columns_values = self._item_indexes.get(i)
            if columns_values:
                yield from columns_values.values()

    def _populate_grid_caches(self, row: int, persistent_index: QPersistentModelIndex, grid: dict, y_offset: int = 0) -> None:
        """
        Helper to fill the cache with all the data of a given row.

        Args:
            row: The row.
            persistent_index: QPersistentModelIndex instance for the row.
            grid: Grid dictionary to caching.
            y_offset: Y offset to apply.
        """
        icon_size = self.iconSize()

        item_w = icon_size.width()
        item_h = icon_size.height()

        cols = self.virtualColumns()

        col_current = row % cols
        virtual_row = row // cols

        px = self._margin + (col_current * (item_w + self._margin))
        y = self._calculate_rows_height(virtual_row)

        rect = QRect(px, y + y_offset, item_w, item_h)
        self._item_rects[persistent_index] = rect

        if virtual_row not in grid:
            grid[virtual_row] = {}

        grid[virtual_row][col_current] = (persistent_index, rect)

    def _calculate_rows_height(self, rows: int) -> int:
        """
        Calculates what the height for a given number of rows.

        Args:
            rows: Quantity to calculate.

        Returns:
            The height.
        """
        icon_size = self.iconSize()
        item_h = icon_size.height()
        return self._margin + ((item_h + self._margin) * rows)

    # -------------------------------------------------------------------------
    # Layout Scheduling & Cache Management
    # -------------------------------------------------------------------------

    def _schedule_layout(self) -> None:
        """Schedule to update the layout."""
        if not self._layout_timer.isActive():
            self._layout_timer.start()

    def _execute_delayed_layout(self) -> None:
        """Update the layout."""
        self.updateGeometries()
        self.viewport().update()

    def _clear_cache(self, *args) -> None:
        """Clear all the cached variables."""
        self._item_rects.clear()
        self._item_indexes.clear()
        self._hover_index = QPersistentModelIndex()
        self.viewport().update()

    def setModel(self, model: typing.Optional[QAbstractItemModel]) -> None:
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
            current_model.layoutChanged.disconnect(self._on_layout_changed)
            current_model.modelReset.disconnect(self._on_model_reset)
            current_model.rowsInserted.disconnect(self._on_rows_inserted)
            current_model.rowsRemoved.disconnect(self._on_rows_removed)
            current_model.dataChanged.disconnect(self._on_data_changed)

            current_model.layoutAboutToBeChanged.disconnect(self._clear_cache)
            current_model.rowsAboutToBeRemoved.disconnect(self._clear_cache)

        # Disconnect from old selection model
        old_selection_model = self.selectionModel()
        if old_selection_model:
            old_selection_model.selectionChanged.disconnect(
                self._on_selection_changed
            )
            old_selection_model.currentChanged.disconnect(self._on_current_changed)

        super().setModel(model)

        if model:
            model.layoutAboutToBeChanged.connect(self._clear_cache)
            model.rowsAboutToBeRemoved.connect(self._clear_cache)

            model.layoutChanged.connect(self._on_layout_changed)
            model.modelReset.connect(self._on_model_reset)
            model.rowsInserted.connect(self._on_rows_inserted)
            model.rowsRemoved.connect(self._on_rows_removed)
            model.dataChanged.connect(self._on_data_changed)

        # Connect to new selection model
        new_selection_model = self.selectionModel()
        if new_selection_model:
            new_selection_model.selectionChanged.connect(self._on_selection_changed)
            new_selection_model.currentChanged.connect(self._on_current_changed)

    @Slot()
    def _on_layout_changed(self) -> None:
        """Handle layout changes to update visual feedback."""
        self._schedule_layout()

    @Slot()
    def _on_model_reset(self) -> None:
        """Handle model reset to update visual feedback."""
        self._schedule_layout()

    @Slot()
    def _on_rows_inserted(self):
        """Handle rows inserted to update visual feedback."""
        self._schedule_layout()

    @Slot()
    def _on_rows_removed(self):
        """Handle rows removed to update visual feedback."""
        self._schedule_layout()

    def _on_data_changed(
        self,
        top_left: QModelIndex,
        _: QModelIndex,
        roles: typing.Optional[list[int]] = None,
    ) -> None:
        """Handle data changes to update visual feedback."""
        if roles is None:
            roles = []

        # [CRUCIAL] Se for uma mudança de dados (como o ícone chegando), força a repintura!
        if not roles or Qt.ItemDataRole.DecorationRole in roles:
            self.update(top_left)

    @Slot()
    def _on_selection_changed(self) -> None:
        """Handle selection changes to update visual feedback."""
        self.viewport().update()

    @Slot()
    def _on_current_changed(self) -> None:
        """Handle current index changes (e.g., from setCurrentIndex) to update visual feedback."""
        self.viewport().update()

    # -------------------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse press events.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if not self._item_rects:
            return

        index = self.indexAt(event.position().toPoint())

        if index.isValid() and event.button() == Qt.MouseButton.LeftButton:
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
            self.itemExited.emit(QPersistentModelIndex(self._hover_index))
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
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}.paintEvent")

        start = time.perf_counter()

        if not self._item_rects:
            return

        painter = QPainter(self.viewport())
        option = QStyleOptionViewItem()
        option.initFrom(self)
        setattr(option, "widget", self)

        vertical_scroll_bar = self.verticalScrollBar()
        scroll_y = vertical_scroll_bar.value()

        item_delegate = self.itemDelegate()

        for p_index, rect in self._visible_items():
            visual_rect = rect.translated(0, -scroll_y)

            logger.debug(f"Paiting {p_index.data(Qt.EditRole)} at {rect.x()}, {rect.y()}.")
            self._init_option(option, p_index, visual_rect)
            item_delegate.paint(painter, option, p_index)

        end = time.perf_counter()
        logger.debug(f"Finished paintEvent in {end - start:.6f} seconds.")

    # -------------------------------------------------------------------------
    # QAbstractItemView Implementation
    # -------------------------------------------------------------------------

    def virtualColumns(self) -> int:
        """
        Calculate the current number of columns.

        Returns:
            Columns count.
        """
        width = self.viewport().width()
        item_w = self.iconSize().width()
        effective_width = width - (2 * self._margin)
        return max(1, effective_width // (item_w + self._margin))

    def updateGeometries(self) -> None:
        """
        Recalculate the layout of item rectangles and update scrollbars.
        Assumes a flat model structure.
        """
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}.updateGeometries")

        start = time.perf_counter()

        if not self.model():
            return

        icon_size = self.iconSize()
        item_h = icon_size.height()

        self._item_rects.clear()
        self._item_indexes.clear()

        rows = list(self._rows(self.rootIndex()))

        for row, persistent_index in enumerate(rows):
            self._populate_grid_caches(row, persistent_index, self._item_indexes)

        rows_count = max(self._item_indexes.keys()) + 1
        content_height = self._calculate_rows_height(rows_count)

        scroll_range = max(0, content_height - self.viewport().height())

        vertical_scroll_bar = self.verticalScrollBar()

        vertical_scroll_bar.setRange(0, scroll_range)
        vertical_scroll_bar.setPageStep(self.viewport().height())
        vertical_scroll_bar.setSingleStep(item_h // 2)

        super().updateGeometries()
        end = time.perf_counter()
        logger.debug(f"Finished updateGeometries in {end - start:.6f} seconds.")

    def visualRect(
        self, index: typing.Union[QModelIndex, QPersistentModelIndex]
    ) -> QRect:
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
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}.indexAt")

        point.setY(point.y() + self.verticalScrollBar().value())
        row, col = self._get_coordinates_at(point)
        logger.debug(f"Looking for index at {row}, {col}")

        cols_p_index = self._item_indexes.get(row)
        if not cols_p_index:
            return QModelIndex()

        result = cols_p_index.get(col)
        if result:
            p_index, _ = result
            logger.debug(f"Found index {p_index}")
            return QModelIndex(p_index)

        return QModelIndex()


    def scrollTo(
        self,
        index: typing.Union[QModelIndex, QPersistentModelIndex],
        hint: QAbstractItemView.ScrollHint = QAbstractItemView.ScrollHint.EnsureVisible,
    ) -> None:
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

    def setSelection(
        self, rect: QRect, command: QItemSelectionModel.SelectionFlag
    ) -> None:
        """
        Apply selection to items within the rectangle.

        Args:
            rect (QRect): The rectangle in viewport coordinates.
            command (QItemSelectionModel.SelectionFlag): The selection command.
        """
        if not self.model():
            return

        selection = QItemSelection()

        # Transform viewport rect to logical coordinates
        scroll_y = self.verticalScrollBar().value()
        logical_rect = rect.translated(0, scroll_y)

        for p_index, item_rect in self._item_rects.items():
            if not p_index.isValid():
                continue

            if item_rect.intersects(logical_rect):
                index = QPersistentModelIndex(p_index)
                if index.isValid():
                    selection.select(index, index)

        self.selectionModel().select(selection, command)

        # Force update to show selection changes
        self.viewport().update()

    def visualRegionForSelection(self, selection: QItemSelection) -> QRegion:
        """
        Return the region covered by the selection.

        Args:
            selection (QItemSelection): The selection to get the region for.

        Returns:
            QRegion: The region covered by the selection in viewport coordinates.
        """
        region = QRegion()

        if not self._item_rects:
            return region

        scroll_y = self.verticalScrollBar().value()

        for index in selection.indexes():
            p_index = QPersistentModelIndex(index)
            item_rect = self._item_rects.get(p_index)

            if item_rect:
                visual_rect = item_rect.translated(0, -scroll_y)
                region = region.united(visual_rect)

        return region

    def isIndexHidden(
        self, index: typing.Union[QModelIndex, QPersistentModelIndex]
    ) -> bool:
        """
        Return True if the item referred to by index is hidden; otherwise returns False.
        """
        # In the simple grid view, usually nothing is hidden unless filtered by model
        # or if we implement filtering here.
        if not index.isValid():
            return True
        return False
