from PySide6.QtCore import QSize, Qt, Signal, QEvent
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QListView, QAbstractScrollArea, QSizePolicy, QWidget

from qextrawidgets.widgets.emoji_picker.emoji_delegate import QEmojiDelegate
from qextrawidgets.proxys.emoji_sort_filter import QEmojiSortFilterProxyModel


class QEmojiGridView(QListView):
    """A customized QListView designed to display emojis in a grid layout.

    Signals:
        left: Emitted when the mouse cursor leaves the grid area.
    """

    left = Signal()

    def __init__(self, parent: QWidget = None, delegate: QEmojiDelegate = None) -> None:
        """Initializes the emoji grid.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
            delegate (QEmojiDelegate, optional): The delegate to use. Defaults to None.
        """
        super().__init__(parent)

        self.setMouseTracking(True)  # Essential for hover to work

        # Default settings
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setUniformItemSizes(True)
        self.setWrapping(True)
        self.setDragEnabled(False)
        self.setSpacing(0)
        self.setTextElideMode(Qt.TextElideMode.ElideNone)

        # Turn off scroll bars (parent should scroll)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Size policy: Expands horizontally, Fixed vertically (based on sizeHint)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)

        # Native adjustment (helps, but sizeHint does the heavy lifting)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        proxy = QEmojiSortFilterProxyModel()
        self.setModel(proxy)

        if delegate is None:
            delegate = QEmojiDelegate(self)

        self.setItemDelegate(delegate)

    def sizeHint(self) -> QSize:
        """Informs the layout of the ideal size for this widget.

        Calculates the height needed to display all items based on the current width.

        Returns:
            QSize: The calculated size hint.
        """
        if self.model() is None or self.model().rowCount() == 0:
            return QSize(0, 0)

        # Available width (if widget hasn't been shown yet, use a default value)
        width = self.width() if self.width() > 0 else 400

        # Grid dimensions
        grid_sz = self.gridSize()
        if grid_sz.isEmpty():
            grid_sz = QSize(40, 40)  # Fallback

        # Mathematical calculation
        item_width = grid_sz.width()
        item_height = grid_sz.height()

        # How many fit per row?
        items_per_row = max(1, width // item_width)

        # How many rows do we need?
        total_items = self.model().rowCount()
        rows = (total_items + items_per_row - 1) // items_per_row  # Ceil division

        height = rows * item_height + 5  # +5 safety padding

        return QSize(width, height)

    def leaveEvent(self, event: QEvent) -> None:
        """Handles the mouse leave event.

        Args:
            event (QEvent): The leave event.
        """
        super().leaveEvent(event)
        self.left.emit()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handles the resize event.

        Triggers a geometry update to recalculate the size hint.

        Args:
            event (QResizeEvent): The resize event.
        """
        super().resizeEvent(event)
        self.updateGeometry()

    def setModel(self, model: QEmojiSortFilterProxyModel) -> None:
        """Sets the model for the emoji grid.

        Args:
            model (QEmojiSortFilterProxyModel): The emoji sort/filter proxy model.
        """
        if not isinstance(model, QEmojiSortFilterProxyModel):
            raise TypeError("Model must be an instance of QEmojiSortFilterProxyModel")
        super().setModel(model)

    def model(self) -> QEmojiSortFilterProxyModel:
        """Returns the current model as a QEmojiSortFilterProxyModel.

        Returns:
            QEmojiSortFilterProxyModel: The current model.
        """
        return super().model()  # type: ignore