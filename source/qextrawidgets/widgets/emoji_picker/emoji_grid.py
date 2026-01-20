import typing

from PySide6.QtCore import QSize, Qt, Signal, QEvent
from PySide6.QtGui import QResizeEvent, QFont, QPixmap
from PySide6.QtWidgets import QListView, QAbstractScrollArea, QSizePolicy, QWidget

from qextrawidgets.utils import get_max_pixel_size, QEmojiFonts
from qextrawidgets.widgets.emoji_picker.emoji_sort_filter import QEmojiSortFilterProxyModel


class QEmojiGrid(QListView):
    """A customized QListView designed to display emojis in a grid layout.

    Signals:
        left: Emitted when the mouse cursor leaves the grid area.
    """

    left = Signal()

    def __init__(self, parent: QWidget = None, emoji_size: int = 40, emoji_margin: float = 0.1, emoji_font: typing.Optional[str] = None) -> None:
        """Initializes the emoji grid.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)

        if emoji_font is None:
            emoji_font = QEmojiFonts.loadTwemojiFont()

        self._emoji_font = emoji_font

        self._emoji_size = emoji_size
        self._emoji_margin_porcentage = emoji_margin  # 10% margin
        self._emoji_pixmap_getter = None

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

        self.updateEmojiSize()
        self.updateEmojiFont()
        self.updateEmojiPixmapGetter()

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

    def setEmojiMarginPorcentage(self, percentage: float) -> None:
        """Sets the margin percentage around each emoji.

        Args:
            percentage (float): The margin percentage (0.0 to 0.5).
        """
        if not (0.0 <= percentage <= 0.5):
            raise ValueError("Margin percentage must be between 0.0 and 0.5")
        self._emoji_margin_porcentage = percentage
        self.updateEmojiMarginPorcentage()

    def updateEmojiMarginPorcentage(self):
        """Updates the emoji margin percentage and refreshes the pixmap getter."""
        self.updateEmojiPixmapGetter()
        self.updateEmojiFont()

    def emojiMarginPorcentage(self) -> float:
        """Returns the current emoji margin percentage.

        Returns:
            float: The margin percentage.
        """
        return self._emoji_margin_porcentage

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

    def setEmojiFont(self, font_family: str) -> None:
        """Sets the font family for the emojis.

        Args:
            font_family (str): Font family name.
        """
        self._emoji_font = font_family
        self.updateEmojiFont()

    def updateEmojiFont(self):
        """Updates the emoji font based on the current settings."""
        font_family = self.emojiFont()
        font = QFont(font_family)
        size = self.emojiSize() * (1 - self.emojiMarginPorcentage())
        pixel_size = get_max_pixel_size("👏", font_family, QSize(size, size))
        font.setPixelSize(pixel_size)
        self.setFont(font)

    def emojiFont(self) -> str:
        """Returns the current emoji font family.

        Returns:
            str: Font family name.
        """
        return self._emoji_font

    def setEmojiSize(self, size: int) -> None:
        """Sets the size for the emoji items.

        Args:
            size (int): The new size.
        """
        if size != self._emoji_size:
            self._emoji_size = size
            self.updateEmojiSize()

    def updateEmojiSize(self):
        """Updates the emoji size and refreshes the grid size."""
        self.updateEmojiFont()
        emoji_size = self.emojiSize()
        size_obj = QSize(emoji_size, emoji_size)
        self.setGridSize(size_obj)
        self.setIconSize(size_obj)
        self.updateEmojiPixmapGetter()

    def emojiSize(self) -> int:
        """Returns the current emoji item size.

        Returns:
            int: The emoji size.
        """
        return self._emoji_size

    def setEmojiPixmapGetter(self, emoji_pixmap_getter: typing.Optional[typing.Callable[[str, int, int, float], QPixmap]]) -> None:
        """Sets a custom function to retrieve emoji pixmaps.

        Args:
            emoji_pixmap_getter (Callable[[str, int, int, float], QPixmap], optional): Function to get emoji pixmaps.
        """
        if emoji_pixmap_getter != self._emoji_pixmap_getter:
            self._emoji_pixmap_getter = emoji_pixmap_getter
            self.updateEmojiPixmapGetter()

    def updateEmojiPixmapGetter(self):
        """Updates the emoji pixmap getter in the model."""
        emoji_pixmap_getter = self.emojiPixmapGetter()
        proxy = self.model()
        if emoji_pixmap_getter:
            emoji_size = self.emojiSize()
            margin = emoji_size * self.emojiMarginPorcentage()
            dpr = self.devicePixelRatio()

            # Fix: Use a factory or default argument to capture the current state
            # to avoid issues with lambda late binding or references
            def make_getter(getter, m, s, d):
                return lambda emoji: getter(emoji, m, s, d)

            proxy.setEmojiPixmapGetter(make_getter(emoji_pixmap_getter, margin, emoji_size, dpr))
        else:
            proxy.setEmojiPixmapGetter(None)

    def emojiPixmapGetter(self) -> typing.Optional[typing.Callable[[str, int, int, float], QPixmap]]:
        """Returns the current emoji pixmap getter function.

        Returns:
            Callable[[str, int, int, float], QPixmap], optional: The pixmap getter function.
        """
        return self._emoji_pixmap_getter