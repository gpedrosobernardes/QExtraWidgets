from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QListView, QAbstractScrollArea, QSizePolicy

from qextrawidgets.utils import QEmojiFonts


class QEmojiGrid(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Assuming you have the Proxy imported or defined

        self.setMouseTracking(True)  # Essential for hover to work

        # Default settings
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setUniformItemSizes(True)
        self.setWrapping(True)
        self.setDragEnabled(False)
        self.setSpacing(0)

        # Turn off scroll bars (parent should scroll)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Size policy: Expands horizontally, Fixed vertically (based on sizeHint)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)

        # Native adjustment (helps, but sizeHint does the heavy lifting)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

    def sizeHint(self) -> QSize:
        """
        Tells the parent Layout the ideal size of this widget.
        Qt calls this automatically when the layout is invalidated.
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

    def resizeEvent(self, event):
        """
        When width changes, the number of rows changes.
        We need to notify the layout to read sizeHint() again.
        """
        super().resizeEvent(event)
        self.updateGeometry()