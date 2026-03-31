import logging
import time
import typing

from PySide6.QtCore import (
    QModelIndex,
    QPersistentModelIndex,
    QSize,
    Qt,
    QRect,
    QAbstractItemModel, QPoint,
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
        self._item_indexes: dict[QPersistentModelIndex, dict[int, dict[int, typing.Tuple[QPersistentModelIndex, QRect]]]] = {}

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

    def isExpanded(self, index: QPersistentModelIndex) -> bool:
        """Return True if the category at index is expanded."""
        return index in self._expanded_items

    def setExpanded(self, index: QPersistentModelIndex, expanded: bool) -> None:
        """Set the expansion state of the category at index."""
        if expanded:
            self._expanded_items.add(index)
        else:
            self._expanded_items.discard(index)

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

    @staticmethod
    def _is_category(
        index: typing.Union[QModelIndex, QPersistentModelIndex]
    ) -> bool:
        """Check if the given index represents a category (header)."""
        return not index.parent().isValid()

    def _init_option(self, option: QStyleOptionViewItem, index: QPersistentModelIndex, visual_rect: QRect) -> None:
        """
        Initialize the style option with expansion state.
        """
        super()._init_option(option, index, visual_rect)

        if self.isExpanded(index):
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

    def _visible_items(self) -> typing.Generator[typing.Tuple[QPersistentModelIndex, QRect]]:
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}._visible_items")

        viewport_rect = self.viewport().rect()
        viewport_rect.translate(0, self.verticalScrollBar().value())
        logger.debug(f"Viewport rect: {viewport_rect}")

        for category_index, grid in self._item_indexes.items():
            category_rect = self._item_rects[category_index]
            # logger.debug(f"Category {category_index.data(Qt.ItemDataRole.EditRole)} rect: {category_rect}")

            if viewport_rect.contains(category_rect):
                yield category_index, category_rect

            if self.isExpanded(category_index) and grid:
                rows_count = max(grid.keys()) + 1

                category_viewport_rect = QRect(viewport_rect)
                category_viewport_rect.translate(0, -category_rect.bottomLeft().y())

                first_row, _ = self._get_coordinates_at(category_viewport_rect.topLeft())
                last_row, _ = self._get_coordinates_at(category_viewport_rect.bottomLeft())
                first_row = max(first_row, 0)

                if first_row > rows_count:
                    continue
                logger.debug(f"Looking for visible items between rows {first_row} and {last_row}")

                for i in range(first_row, last_row + 1):
                    columns_values = grid.get(i)
                    if columns_values:
                        yield from columns_values.values()

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
        p_index = QPersistentModelIndex(index)

        if event.button() == Qt.MouseButton.LeftButton and p_index.isValid() and self._is_category(p_index):
            self.setExpanded(p_index, not self.isExpanded(p_index))
            event.accept()
            return

        super().mousePressEvent(event)

    # -------------------------------------------------------------------------
    # QAbstractItemView Implementation
    # -------------------------------------------------------------------------

    def updateGeometries(self) -> None:
        """
        Recalculate the layout of item rectangles and update scrollbars.
        """
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}.updateGeometries")

        start = time.perf_counter()
        model = self.model()

        if not model:
            return

        self._item_rects.clear()
        width = self.viewport().width()
        y = 0

        root = self.rootIndex()

        row_count = model.rowCount(root)

        for r in range(row_count):
            cat_index = model.index(r, 0, root)
            if not cat_index.isValid():
                continue

            cat_persistent_index = QPersistentModelIndex(cat_index)

            self._item_rects[cat_persistent_index] = QRect(
                0, y, width, self._header_height
            )

            self._item_indexes[cat_persistent_index] = {}

            y += self._header_height

            rows = list(self._rows(cat_index))

            if self.isExpanded(cat_persistent_index) and rows:
                for row, persistent_index in enumerate(rows):
                    self._populate_grid_caches(row, persistent_index, self._item_indexes[cat_persistent_index], y)

                rows_count = max(self._item_indexes[cat_persistent_index].keys()) + 1
                logger.debug(f"Rows count: {rows_count}")
                y += self._calculate_rows_height(rows_count)
                logger.debug(f"Rows height: {self._header_height}")

        content_height = y
        scroll_range = max(0, content_height - self.viewport().height())

        vertical_scroll_bar = self.verticalScrollBar()

        vertical_scroll_bar.setRange(0, scroll_range)
        vertical_scroll_bar.setPageStep(self.viewport().height())
        vertical_scroll_bar.setSingleStep(self._header_height)

        end = time.perf_counter()
        logger.debug(f"Finished updateGeometries in {end - start:.6f} seconds.")

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
        return not self.isExpanded(QPersistentModelIndex(index.parent()))

    def indexAt(self, point: QPoint) -> QModelIndex:
        """
        Return the model index of the item at the viewport coordinates point.

        Args:
            point (QPoint): The coordinates in the viewport.

        Returns:
            QModelIndex: The index at the given point, or valid if not found.
        """
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}.indexAt")

        for category_index, grid in self._item_indexes.items():
            real_point = point + QPoint(0, self.verticalScrollBar().value())
            logger.debug(f"Looking for index at {real_point}")

            category_rect = self._item_rects[category_index]
            logger.debug(f"Verifying if point is on category {category_rect}")
            if category_rect.contains(real_point):
                logger.debug(f"Yes, point is on category {category_rect}")
                return QModelIndex(category_index)

            if self.isExpanded(category_index):
                row, col = self._get_coordinates_at(real_point - category_rect.bottomLeft())
                logger.debug(f"Looking for index at {row}, {col}")

                cols_p_index = grid.get(row)
                if not cols_p_index:
                    continue

                result = cols_p_index.get(col)
                if result:
                    p_index, rect = result
                    logger.debug(f"Found index {p_index}")
                    if rect.contains(real_point):
                        return QModelIndex(p_index)

        return QModelIndex()
