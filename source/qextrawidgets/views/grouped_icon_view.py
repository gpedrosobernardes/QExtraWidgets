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
    QTimer
)
from PySide6.QtGui import QCursor, QPainter, QMouseEvent
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

    def setIconSize(self, size: QSize) -> None:
        super().setIconSize(size)
        self._schedule_layout()

    def setMargin(self, margin: int) -> None:
        if self._margin == margin:
            return
        self._margin = margin
        self._schedule_layout()

    def margin(self) -> int:
        return self._margin

    def setHeaderHeight(self, height: int) -> None:
        if self._header_height == height:
            return
        self._header_height = height
        self._schedule_layout()

    def headerHeight(self) -> int:
        return self._header_height

    # -------------------------------------------------------------------------
    # Internal Logic Helpers
    # -------------------------------------------------------------------------

    def _is_category(self, index: QModelIndex) -> bool:
        return index.isValid() and not index.parent().isValid()

    def _is_item(self, index: QModelIndex) -> bool:
        return index.isValid() and index.parent().isValid()

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
                self.itemExited.emit(QModelIndex(self._hover_index))

            self._hover_index = new_persistent

            if self._hover_index.isValid():
                self.itemEntered.emit(QModelIndex(self._hover_index))

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
        self.viewport().update()

    def setModel(self, model: Optional[QAbstractItemModel]) -> None:
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
        self._schedule_layout()

    def _on_rows_inserted(self, parent, start, end):
        self._schedule_layout()

    def _on_rows_removed(self, parent, start, end):
        self._schedule_layout()

    def _on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: list[int] = None) -> None:
        if roles is None:
            roles = []

        # Se for uma mudança estrutural ou de expansão, recalcula o layout
        if not roles or QEmojiCategoryItem.ExpansionStateRole in roles:
            self._schedule_layout()
        # [CRUCIAL] Se for uma mudança de dados (como o ícone chegando), força a repintura!
        elif Qt.ItemDataRole.DecorationRole in roles:
            self.update(top_left)


    # -------------------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self._item_rects: return

        index = self.indexAt(event.position().toPoint())

        if index.isValid() and event.button() == Qt.MouseButton.LeftButton:
            if self._is_category(index):
                current_state = bool(index.data(QEmojiCategoryItem.ExpansionStateRole))
                self.model().setData(index, not current_state, QEmojiCategoryItem.ExpansionStateRole)
                event.accept()
                return
            elif self._is_item(index):
                self.itemClicked.emit(index)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._recalculate_hover()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        if self._hover_index.isValid():
            self.itemExited.emit(QModelIndex(self._hover_index))
        self._hover_index = QPersistentModelIndex()
        self.viewport().update()
        super().leaveEvent(event)

    # noinspection PyUnresolvedReferences
    def paintEvent(self, event: QEvent) -> None:
        if not self._item_rects:
            return

        painter = QPainter(self.viewport())
        region = event.rect()
        scroll_y = self.verticalScrollBar().value()

        option = QStyleOptionViewItem()
        option.initFrom(self)

        for p_index, rect in self._item_rects.items():
            if not p_index.isValid():
                continue

            index = QModelIndex(p_index)
            if not index.isValid():
                continue

            visual_rect = rect.translated(0, -scroll_y)

            if not visual_rect.intersects(region):
                continue

            option.rect = visual_rect
            option.state = QStyle.State.State_None

            if self.isEnabled():
                option.state |= QStyle.State.State_Enabled
            if self.selectionModel().isSelected(index):
                option.state |= QStyle.State.State_Selected

            if p_index == self._hover_index:
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

            is_expanded = bool(cat_index.data(QEmojiCategoryItem.ExpansionStateRole))

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

    def visualRect(self, index: QModelIndex) -> QRect:
        p_index = QPersistentModelIndex(index)
        rect = self._item_rects.get(p_index)
        if rect:
            return rect.translated(0, -self.verticalScrollBar().value())
        return QRect()

    def indexAt(self, point: QPoint) -> QModelIndex:
        if not self._item_rects:
            return QModelIndex()

        real_point = point + QPoint(0, self.verticalScrollBar().value())
        for p_index, rect in self._item_rects.items():
            if rect.contains(real_point):
                return QModelIndex(p_index)
        return QModelIndex()

    def scrollTo(self, index: QModelIndex, hint=QAbstractItemView.ScrollHint.EnsureVisible) -> None:
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
            center_target = item_top - (viewport_height / 2) + (rect.height() / 2)
            self.verticalScrollBar().setValue(center_target)

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