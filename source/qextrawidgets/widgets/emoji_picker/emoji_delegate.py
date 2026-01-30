import typing
from functools import lru_cache

from PySide6.QtCore import QSize, Qt, QModelIndex, Signal
from PySide6.QtGui import QPixmap, QFont, QIcon
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QWidget

from qextrawidgets.utils import get_max_pixel_size, QEmojiFonts


class QEmojiDelegate(QStyledItemDelegate):
    """A delegate for rendering emojis in the QEmojiPicker.

    Handles custom rendering of emojis, including support for custom pixmaps
    (e.g., Twemoji) and standard font-based rendering.
    
    Signals:
        emojiSizeChanged (int): Emitted when the emoji size changes.
    """
    
    emojiSizeChanged = Signal(int)
    emojiPixmapGetterChanged = Signal()
    emojiFontChanged = Signal(str)

    def __init__(self, parent: typing.Optional[QWidget] = None,
                 emoji_size: int = 40,
                 emoji_margin: float = 0.1,
                 emoji_font: typing.Optional[str] = None,
                 emoji_pixmap_getter: typing.Optional[typing.Callable[[str, int, int, float], QPixmap]] = None) -> None:
        """Initializes the emoji delegate.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
            emoji_size (int, optional): Size of individual emoji items. Defaults to 40.
            emoji_margin (float, optional): Margin percentage around emojis. Defaults to 0.1.
            emoji_font (str, optional): Font family to use for emojis. If None, Twemoji is loaded. Defaults to None.
            emoji_pixmap_getter (Callable, optional): Function to retrieve emoji pixmaps. Defaults to None.
        """
        super().__init__(parent)
        
        if emoji_font is None:
            emoji_font = QEmojiFonts.loadTwemojiFont()
            
        self._emoji_size = emoji_size
        self._emoji_margin_percentage = emoji_margin
        self._emoji_font = emoji_font
        self._emoji_pixmap_getter = emoji_pixmap_getter

    # noinspection PyUnresolvedReferences
    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """Initializes the style option with the emoji data.

        Args:
            option (QStyleOptionViewItem): The style option to initialize.
            index (QModelIndex): The model index.
        """
        super().initStyleOption(option, index)

        if not index.isValid():
            return

        emoji = index.data(Qt.ItemDataRole.EditRole)
        if not emoji:
            return

        if self._emoji_pixmap_getter:
            # Calculate effective content size based on margin
            margin_pixels = int(self._emoji_size * self._emoji_margin_percentage)
            content_size = self._emoji_size

            # Ensure content size is positive
            content_size = max(1, content_size)

            # Custom Pixmap Rendering
            dpr = 1.0
            if option.widget:
                dpr = option.widget.devicePixelRatio()
            
            option.icon = self.getEmojiIcon(emoji, margin_pixels, self._emoji_size, dpr)
            option.features |= QStyleOptionViewItem.HasDecoration
            option.text = ""  # Hide text
            option.decorationSize = QSize(content_size, content_size)
            option.displayAlignment = Qt.AlignmentFlag.AlignCenter
            
        else:
            # Calculate effective content size based on margin
            margin_pixels = int(self._emoji_size * self._emoji_margin_percentage)
            content_size = self._emoji_size - margin_pixels

            # Ensure content size is positive
            content_size = max(1, content_size)

            # Font Rendering
            option.text = emoji
            option.features |= QStyleOptionViewItem.HasDisplay
            option.features &= ~QStyleOptionViewItem.HasDecoration  # No icon
            
            font = QFont(self._emoji_font)
            # Calculate pixel size to fit within the content area
            pixel_size = get_max_pixel_size(emoji, self._emoji_font, QSize(content_size, content_size))
            font.setPixelSize(pixel_size)
            
            option.font = font
            option.displayAlignment = Qt.AlignmentFlag.AlignCenter

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        """Returns the size hint for the item.

        Args:
            option (QStyleOptionViewItem): The style options.
            index (QModelIndex): The model index.

        Returns:
            QSize: The size hint.
        """
        return QSize(self._emoji_size, self._emoji_size)

    # --- Setters and Getters ---

    def setEmojiSize(self, size: int) -> None:
        """Sets the size for the emoji items.

        Args:
            size (int): The new size.
        """
        if self._emoji_size != size:
            self._emoji_size = size
            self.emojiSizeChanged.emit(size)

    def emojiSize(self) -> int:
        """Returns the current emoji item size.

        Returns:
            int: The emoji size.
        """
        return self._emoji_size

    def setEmojiMarginPercentage(self, percentage: float) -> None:
        """Sets the margin percentage around emojis.

        Args:
            percentage (float): Margin percentage (0.0 to 0.5).
        """
        self._emoji_margin_percentage = percentage

    def emojiMarginPercentage(self) -> float:
        """Returns the current margin percentage.

        Returns:
            float: Margin percentage.
        """
        return self._emoji_margin_percentage

    def setEmojiFont(self, font_family: str) -> None:
        """Sets the font family for the emojis.

        Args:
            font_family (str): Font family name.
        """
        if self._emoji_font != font_family:
            self._emoji_font = font_family
            self.emojiFontChanged.emit(font_family)

    def emojiFont(self) -> str:
        """Returns the current emoji font family.

        Returns:
            str: Font family name.
        """
        return self._emoji_font

    def setEmojiPixmapGetter(self, getter: typing.Optional[typing.Callable[[str, int, int, float], QPixmap]]) -> None:
        """Sets the function used to retrieve emoji pixmaps.

        Args:
            getter (Callable, optional): Pixmap getter function.
        """
        if self._emoji_pixmap_getter != getter:
            self._emoji_pixmap_getter = getter
            self.emojiPixmapGetterChanged.emit()

    def emojiPixmapGetter(self) -> typing.Optional[typing.Callable[[str, int, int, float], QPixmap]]:
        """Returns the current emoji pixmap getter function."""
        return self._emoji_pixmap_getter

    @lru_cache(maxsize=2048)
    def getEmojiIcon(self, emoji: str, margin: int, size: int, dpr: float):
        return QIcon(self._emoji_pixmap_getter(emoji, margin, size, dpr))
