import typing
from PySide6.QtCore import (
    QModelIndex,
    QPersistentModelIndex,
    QSize,
    Qt,
    QRect,
    QPoint,
    QAbstractItemModel,
)
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QAbstractItemView, QWidget, QStyleOptionViewItem, QStyle

from qextrawidgets.widgets.delegates.grouped_icon_delegate import QGroupedIconDelegate
from qextrawidgets.widgets.views.grid_icon_view import QGridIconView


class QGroupedIconView(QGridIconView):
    """
    A custom item view that displays categories as headers (accordion style)
    and children items in a grid layout using icons.

    Uses QPersistentModelIndex for internal caching and QTimer for layout debouncing.
    The expansion state is stored in the model using ExpansionStateRole.
    """

    def __init__(
        self,
        parent: typing.Optional[QWidget] = None,
        icon_size: QSize = QSize(100, 100),
        margin: int = 8,
        header_height: int = 36,
    ):
        """
        Initialize the QGroupedIconView.

        Args:
            parent (Optional[QWidget]): The parent widget.
            icon_size (QSize): The size of the icons in the grid. Defaults to 100x100.
            margin (int): The margin between items and headers. Defaults to 8.
            header_height (int): The height of the category headers. Defaults to 36.
        """
        super().__init__(parent, icon_size=icon_size, margin=margin)

        # View State
        self._expanded_items: set[QPersistentModelIndex] = set()

        # Layout Configuration
        self._header_height: int = header_height

        # Set Delegate
        self.setItemDelegate(QGroupedIconDelegate(self, arrow_icon=None))

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def itemDelegate(
        self, _: typing.Union[QModelIndex, QPersistentModelIndex, None] = None
    ) -> QGroupedIconDelegate:
        """Returns the item delegate used by the view."""
        return typing.cast(QGroupedIconDelegate, super().itemDelegate())

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

    def _is_category(
        self, index: typing.Union[QModelIndex, QPersistentModelIndex]
    ) -> bool:
        """Check if the given index represents a category (header)."""
        return index.isValid() and not index.parent().isValid()

    def _is_item(self, index: typing.Union[QModelIndex, QPersistentModelIndex]) -> bool:
        """Check if the given index represents a child item."""
        return index.isValid() and index.parent().isValid()

    def _init_option(self, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """
        Initialize the style option with expansion state.
        """
        super()._init_option(option, index)
        if self._is_category(index) and self.isExpanded(index):
            state = typing.cast(QStyle.StateFlag, option.state)
            state |= QStyle.StateFlag.State_Open
            setattr(option, "state", state)

    def _clear_cache(self, *args) -> None:
        super()._clear_cache(*args)
        # Clean up invalid persistent indices from expansion set
        self._expanded_items = {pi for pi in self._expanded_items if pi.isValid()}

    def setModel(self, model: typing.Optional[QAbstractItemModel]) -> None:
        """
        Set the model for the view.

        Connects to necessary signals for handling layout updates and structural changes.

        Args:
            model (Optional[QAbstractItemModel]): The model to be set.
        """
        super().setModel(model)
        self._expanded_items.clear()

    def _on_model_reset(self) -> None:
        self._expanded_items.clear()
        super()._on_model_reset()

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
        if not self._item_rects:
            return

        index = self.indexAt(event.position().toPoint())

        if index.isValid() and event.button() == Qt.MouseButton.LeftButton:
            if self._is_category(index):
                self.setExpanded(index, not self.isExpanded(index))
                event.accept()
                return
            elif self._is_item(index):
                # The base class emits itemClicked, but we also want to handle it here explicitly if needed.
                # Actually base class handles itemClicked emission.
                # But we just return if handled category.
                pass

        super().mousePressEvent(event)

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

            self._item_rects[QPersistentModelIndex(cat_index)] = QRect(
                0, y, width, self._header_height
            )
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
                        self._item_rects[QPersistentModelIndex(child)] = QRect(
                            px, y, item_w, item_h
                        )

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

        # We don't call super().updateGeometries() because we fully implemented it here for the grouped view

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

        # [CHANGED] Hybrid Behavior:
        # 1. Categories: Always force scroll to top (Classic Behavior).
        if self._is_category(index):
            self.verticalScrollBar().setValue(rect.y())
            return

        # 2. Items: Smart scroll (New Behavior) - Only scroll if needed.
        # Use base class implementation for items
        super().scrollTo(index, hint)

    def isIndexHidden(
        self, index: typing.Union[QModelIndex, QPersistentModelIndex]
    ) -> bool:
        """
        Return True if the item referred to by index is hidden; otherwise returns False.
        """
        if not index.isValid():
            return True

        if self._is_category(index):
            return False

        # Check if parent category is expanded
        return not self.isExpanded(index.parent())
