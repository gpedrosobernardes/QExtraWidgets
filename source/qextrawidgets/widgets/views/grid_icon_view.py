import typing

from PySide6.QtCore import (
    QModelIndex,
    QPersistentModelIndex,
    QSize,
    Qt,
    QRect,
    QPoint,
    Signal,
    QAbstractItemModel,
    QTimer,
    QItemSelection,
    QItemSelectionModel,
    Slot,
)
from PySide6.QtGui import QCursor, QPainter, QRegion, QPaintEvent, QMouseEvent
from PySide6.QtWidgets import QAbstractItemView, QStyleOptionViewItem, QStyle, QWidget

from qextrawidgets.core.utils.system_utils import debug
from qextrawidgets.widgets.delegates.grid_icon_delegate import QGridIconDelegate


class QGridIconView(QAbstractItemView):
    exited = Signal(QModelIndex)

    def __init__(
            self,
            parent: typing.Optional[QWidget] = None,
            icon_size: QSize = QSize(100, 100),
            margin: int = 8,
            padding: int = 4
    ):
        super().__init__(parent)

        self._model_column = 0
        self._hovered_index = QModelIndex()
        self._margin = margin
        self._padding = padding
        self._hidden_rows: typing.Set[int] = set()

        self._layout_timer = QTimer(self)
        self._layout_timer.setSingleShot(True)
        self._layout_timer.setInterval(0)
        self._layout_timer.timeout.connect(self._execute_delayed_layout)

        self.setIconSize(icon_size)
        self.setMouseTracking(True)
        # self.setAutoScroll(False)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setItemDelegate(QGridIconDelegate(self))
        self.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)

    def setPadding(self, padding: int):
        if self._padding != padding:
            self._padding = padding
            self._schedule_layout()

    def padding(self) -> int:
        return self._padding

    def tileSizeHint(self) -> QSize:
        icon_size = self.iconSize()
        height = icon_size.height() + self._padding * 2 + self._margin * 2
        width = icon_size.width() + self._padding * 2 + self._margin * 2
        return QSize(width, height)

    def itemSizeHint(self) -> QSize:
        icon_size = self.iconSize()
        height = icon_size.height() + self._padding * 2
        width = icon_size.width() + self._padding * 2
        return QSize(width, height)

    def itemDelegate(self, _ = None) -> QGridIconDelegate:
        return typing.cast(QGridIconDelegate, super().itemDelegate())

    def setMargin(self, margin: int):
        if self._margin != margin:
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
                self._hidden_rows.add(row)
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

    @debug
    def scrollContentsBy(self, dx, dy, **kwargs):
        self.viewport().scroll(dx, dy)
        pos = self.viewport().mapFromGlobal(QCursor.pos())
        index = self.indexAt(pos)
        self._set_hovered_index(index)

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

            current_model.layoutAboutToBeChanged.disconnect(self._on_layout_changed)
            current_model.rowsAboutToBeRemoved.disconnect(self._on_layout_changed)

        # Disconnect from old selection model
        old_selection_model = self.selectionModel()
        if old_selection_model:
            old_selection_model.selectionChanged.disconnect(
                self._on_selection_changed
            )

        super().setModel(model)

        if model:
            model.layoutAboutToBeChanged.connect(self._on_layout_changed)
            model.rowsAboutToBeRemoved.connect(self._on_layout_changed)

            model.layoutChanged.connect(self._on_layout_changed)
            model.modelReset.connect(self._on_model_reset)
            model.rowsInserted.connect(self._on_rows_inserted)
            model.rowsRemoved.connect(self._on_rows_removed)
            model.dataChanged.connect(self._on_data_changed)

        # Connect to new selection model
        new_selection_model = self.selectionModel()
        if new_selection_model:
            new_selection_model.selectionChanged.connect(self._on_selection_changed)

    @Slot()
    def _on_layout_changed(self):
        """Handle layout changes to update visual feedback."""
        self._schedule_layout()

    @Slot()
    def _on_model_reset(self):
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

    def _on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: list[int]):
        if Qt.ItemDataRole.EditRole in roles or Qt.ItemDataRole.DecorationRole in roles:
            top_rect = self.tileRect(top_left)
            bottom_rect = self.tileRect(bottom_right)

            self.viewport().update(
                top_rect.united(bottom_rect)
            )

    @Slot()
    def _on_selection_changed(self):
        """Handle selection changes to update visual feedback."""
        selection = self.selectionModel().selection()
        region = self.visualRegionForSelection(selection)
        for rect in region:
            self.viewport().update(rect)

    def _set_hovered_index(self, index: QModelIndex) -> None:
        if index != self._hovered_index:
            old = self._hovered_index
            self._hovered_index = index

            self.exited.emit(index)
            self.viewport().update(self.tileRect(old))
            self.viewport().update(self.tileRect(index))

    # -------------------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------------------

    def mouseMoveEvent(self, event: QMouseEvent):
        index = self.indexAt(event.position().toPoint())
        self._set_hovered_index(index)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        index = self.indexAt(event.position().toPoint())
        if not index.isValid():
            return

        modifiers = event.modifiers()

        selection_model = self.selectionModel()

        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            command = QItemSelectionModel.SelectionFlag.Select

            last_index = selection_model.currentIndex()
            last_index_rect = self.visualRect(last_index)
            index_rect = self.visualRect(index)

            rect_to_select = index_rect.united(last_index_rect)
            self.setSelection(rect_to_select, command)
            selection_model.setCurrentIndex(index, command)

        else:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                command = QItemSelectionModel.SelectionFlag.Toggle
            else:
                command = QItemSelectionModel.SelectionFlag.ClearAndSelect

            selection_model.select(index, command)
            selection_model.setCurrentIndex(index, QItemSelectionModel.SelectionFlag.NoUpdate)

    @debug
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self.viewport())
        option = QStyleOptionViewItem()
        self.initViewItemOption(option)
        option.widget = self.viewport()

        # cacheia fora do loop
        scroll_y = self.verticalScrollBar().value()
        virtual_columns = self.virtualColumns()
        tile_size = self.tileSizeHint()
        item_size = self.itemSizeHint()
        is_enabled = self.isEnabled()
        selection_model = self.selectionModel()
        hovered = self._hovered_index
        base_state = QStyle.StateFlag.State_Enabled if is_enabled else QStyle.StateFlag.State_None

        dirty_rect = event.rect().translated(0, scroll_y)

        first_virtual_point = self.virtualPointAt(dirty_rect.topLeft())
        first_row = self._model_row(first_virtual_point, virtual_columns)
        last_virtual_point = self.virtualPointAt(dirty_rect.bottomRight())
        last_row = self._model_row(last_virtual_point, virtual_columns)

        model = self.model()
        item_delegate = self.itemDelegate()

        for row in range(first_row, last_row + 1):
            index = model.index(row, self.modelColumn())
            if index.isValid():
                virtual_point = self._virtual_point(row, virtual_columns)
                rect = self._visual_rect(virtual_point, tile_size, item_size, scroll_y)

                state = base_state
                if selection_model.isSelected(index):
                    state |= QStyle.StateFlag.State_Selected
                if index == hovered:
                    state |= QStyle.StateFlag.State_MouseOver

                option.rect = rect
                option.state = state
                item_delegate.paint(painter, option, index)

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
        tile_width = self.tileSizeHint().width()
        return max(1, width // tile_width)

    @debug
    def updateGeometries(self, **kwargs):
        """
        Recalculate the layout of item rectangles and update scrollbars.
        Assumes a flat model structure.
        """
        model = self.model()

        if model is None:
            return

        tile_height = self.tileSizeHint().height()
        virtual_point = self.virtualPoint(model.rowCount() - 1)

        content_height = tile_height * (virtual_point.y() + 1)

        viewport_height = self.viewport().height()
        scroll_range = max(0, content_height - viewport_height)

        vertical_scroll_bar = self.verticalScrollBar()
        vertical_scroll_bar.setRange(0, scroll_range)
        vertical_scroll_bar.setPageStep(viewport_height)
        vertical_scroll_bar.setSingleStep(tile_height // 2)

        super().updateGeometries()

    def visualRect(self, index: typing.Union[QModelIndex, QPersistentModelIndex]) -> QRect:
        """
        Return the rectangle on the viewport occupied by the item at index.

        Args:
            index (QModelIndex | QPersistentModelIndex): The index of the item.

        Returns:
            QRect: The visual rectangle.
        """
        virtual_point = self.virtualPoint(index.row())
        vertical_scroll_bar = self.verticalScrollBar()
        scroll_y = vertical_scroll_bar.value()
        return self._visual_rect(virtual_point, self.tileSizeHint(), self.itemSizeHint(), scroll_y)

    def _visual_rect(self, virtual_point: QPoint, tile_size: QSize, item_size: QSize, scroll_y: int) -> QRect:
        x = virtual_point.x() * tile_size.width() + self._margin
        y = virtual_point.y() * tile_size.height() + self._margin
        return QRect(QPoint(x, y - scroll_y), item_size)

    def tileRect(self, index: typing.Union[QModelIndex, QPersistentModelIndex]) -> QRect:
        virtual_point = self.virtualPoint(index.row())
        tile_size = self.tileSizeHint()
        x = virtual_point.x() * tile_size.width()
        y = virtual_point.y() * tile_size.height()
        vertical_scroll_bar = self.verticalScrollBar()
        scroll_y = vertical_scroll_bar.value()
        return QRect(QPoint(x, y - scroll_y), tile_size)

    def indexAt(self, point: QPoint) -> QModelIndex:
        """
        Return the model index of the item at the viewport coordinates point.

        Args:
            point (QPoint): The coordinates in the viewport.

        Returns:
            QModelIndex: The index at the given point, or valid if not found.
        """
        vertical_scroll_bar = self.verticalScrollBar()
        point.setY(point.y() + vertical_scroll_bar.value())
        virtual_point = self.virtualPointAt(point)
        row = self.modelRow(virtual_point)
        index = self.model().index(row, self.modelColumn())
        visual_rect = self.visualRect(index)
        visual_rect.translate(0, vertical_scroll_bar.value())
        if visual_rect.contains(point):
            return index
        else:
            return QModelIndex()

    @debug
    def scrollTo(
        self,
        index: typing.Union[QModelIndex, QPersistentModelIndex],
        hint: QAbstractItemView.ScrollHint = QAbstractItemView.ScrollHint.EnsureVisible,
        **kwargs
    ) -> None:
        """
        Scroll the view to ensure the item at index is visible.

        Args:
            index (QModelIndex | QPersistentModelIndex): The index to scroll to.
            hint (QAbstractItemView.ScrollHint): The scroll hint.
        """
        rect = self.visualRect(index)
        vertical_scroll_bar = self.verticalScrollBar()
        scroll_y = vertical_scroll_bar.value()
        rect.translate(0, scroll_y)

        if not rect:
            return

        scroll_val = self.verticalScrollBar().value()
        viewport_height = self.viewport().height()

        item_top = rect.y()
        item_bottom = rect.bottom()

        if hint == QAbstractItemView.ScrollHint.EnsureVisible:
            if item_bottom <= scroll_val or item_top >= scroll_val + viewport_height:
                if item_top < scroll_val:
                    self.verticalScrollBar().setValue(item_top)
                else:
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

    def moveCursor(self, cursor_action: QAbstractItemView.CursorAction, modifiers: Qt.KeyboardModifier) -> QModelIndex:
        """
        Move the cursor in response to key navigation (Not implemented).

        Returns:
            QModelIndex: An invalid index.
        """
        current = self.selectionModel().currentIndex()

        model = self.model()

        if not current.isValid():
            return model.index(0, self.modelColumn())

        current_row = current.row()
        virtual_columns = self.virtualColumns()

        moves = {
            QAbstractItemView.CursorAction.MoveLeft: -1,
            QAbstractItemView.CursorAction.MoveRight: +1,
            QAbstractItemView.CursorAction.MoveUp: -virtual_columns,
            QAbstractItemView.CursorAction.MoveDown: +virtual_columns,
        }

        try:
            move = moves[cursor_action]
        except KeyError:
            pass
        else:
            new_row = current_row + move
            index = model.index(new_row, self.modelColumn())
            if index.isValid():
                return index
            else:
                return model.index(current_row, self.modelColumn())

        if cursor_action == QAbstractItemView.CursorAction.MoveHome:
            return model.index(0, self.modelColumn())

        elif cursor_action == QAbstractItemView.CursorAction.MoveEnd:
            return model.index(model.rowCount(), self.modelColumn())

        else:
            return model.index(0, self.modelColumn())

    def setSelection(self, rect: QRect, command: QItemSelectionModel.SelectionFlag):
        """
        Apply selection to items within the rectangle.

        Args:
            rect (QRect): The rectangle in viewport coordinates.
            command (QItemSelectionModel.SelectionFlag): The selection command.
        """
        if not self.model():
            return

        selection = QItemSelection()

        scroll_y = self.verticalScrollBar().value()
        logical_rect = rect.translated(0, scroll_y)

        start_virtual_point = self.virtualPointAt(logical_rect.topLeft())
        end_virtual_point = self.virtualPointAt(logical_rect.bottomRight())

        model = self.model()
        virtual_rows = set(range(start_virtual_point.y(), end_virtual_point.y() + 1))
        virtual_columns = set(range(start_virtual_point.x(), end_virtual_point.x() + 1))

        virtual_columns_count = self.virtualColumns()

        for virtual_row in virtual_rows:
            for virtual_column in virtual_columns:
                virtual_point = QPoint(virtual_column, virtual_row)
                row = self._model_row(virtual_point, virtual_columns_count)
                index = model.index(row, self.modelColumn())
                selection.select(index, index)

        self.selectionModel().select(selection, command)

    def visualRegionForSelection(self, selection: QItemSelection) -> QRegion:
        """
        Return the region covered by the selection.

        Args:
            selection (QItemSelection): The selection to get the region for.

        Returns:
            QRegion: The region covered by the selection in viewport coordinates.
        """
        region = QRegion()

        for selection_range in selection:
            top = selection_range.top()
            bottom = selection_range.bottom()

            first_rect = self.tileRect(
                self.model().index(top, self.modelColumn())
            )

            last_rect = self.tileRect(
                self.model().index(bottom, self.modelColumn())
            )

            region += QRect(
                first_rect.topLeft(),
                last_rect.bottomRight(),
            )

        return region

    def isIndexHidden(self, index: typing.Union[QModelIndex, QPersistentModelIndex]) -> bool:
        """
        Return True if the item referred to by index is hidden; otherwise returns False.
        """
        # In the simple grid view, usually nothing is hidden unless filtered by model
        # or if we implement filtering here.
        if not index.isValid():
            return True
        return False

    def setModelColumn(self, column: int):
        """
        Set the model column from which item data is read.

        Args:
            column (int): Zero-based column index to use when querying the model.
        """
        if column != self._model_column:
            self._model_column = column

    def modelColumn(self) -> int:
        """
        Return the model column currently used to read item data.

        Returns:
            int: Zero-based column index.
        """
        return self._model_column

    def modelRow(self, virtual_point: QPoint) -> int:
        virtual_columns = self.virtualColumns()
        return self._model_row(virtual_point, virtual_columns)

    def _model_row(self, virtual_point: QPoint, virtual_columns: int) -> int:
        return virtual_point.y() * virtual_columns + virtual_point.x()

    def virtualPoint(self, row: int) -> QPoint:
        virtual_columns = self.virtualColumns()
        return self._virtual_point(row, virtual_columns)

    def _virtual_point(self, row: int, virtual_columns: int) -> QPoint:
        virtual_row = row // virtual_columns
        virtual_column = row % virtual_columns
        return QPoint(virtual_column, virtual_row)

    def virtualPointAt(self, point: QPoint) -> QPoint:
        tile_size = self.tileSizeHint()
        col = point.x() // tile_size.width()
        row = point.y() // tile_size.height()
        return QPoint(col, row)
