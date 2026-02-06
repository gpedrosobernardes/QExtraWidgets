import typing
from functools import partial

from PySide6.QtCore import Signal, QSize
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QMenu, QWidgetAction, QWidget

from qextrawidgets.core.utils.twemoji_image_provider import QTwemojiImageProvider
from qextrawidgets.gui.items import QEmojiItem
from qextrawidgets.gui.models.emoji_picker_model import QEmojiPickerModel
from qextrawidgets.widgets.miscellaneous.emoji_picker import QEmojiPicker


class QEmojiPickerMenu(QMenu):
    """A menu that displays a QEmojiPicker.

    Signals:
        picked (str): Emitted when an emoji is selected.
    """

    picked = Signal(QEmojiItem)

    def __init__(
            self,
            parent: typing.Optional[QWidget] = None,
            model: typing.Optional[QEmojiPickerModel] = None,
            emoji_pixmap_getter: typing.Union[str, QFont, typing.Callable[[str], QPixmap]] = partial(
                QTwemojiImageProvider.getPixmap, margin=0, size=128),
            emoji_label_size: QSize = QSize(32, 32)) -> None:
        """Initialize the emoji picker menu.

        Args:
            parent (QWidget, optional): The parent widget.
            model (QEmojiPickerModel, optional): Custom emoji model. Defaults to None.
            emoji_pixmap_getter (Union[str, QFont, Callable[[str], QPixmap]], optional):
                Method or font to generate emoji pixmaps. Defaults to EmojiImageProvider.getPixmap.
            emoji_label_size (QSize, optional): Size of the preview emoji label. Defaults to QSize(32, 32).
        """
        super().__init__(parent)
        self._picker = QEmojiPicker(model, emoji_pixmap_getter, emoji_label_size)
        self._picker.picked.connect(self._on_picked)

        action = QWidgetAction(self)
        action.setDefaultWidget(self._picker)
        self.addAction(action)

    def picker(self) -> QEmojiPicker:
        """Returns the internal emoji picker widget.

        Returns:
            QEmojiPicker: The emoji picker widget.
        """
        return self._picker

    def _on_picked(self, item: QEmojiItem) -> None:
        """Handles the emoji picked signal.

        Args:
            item (QEmojiItem): The picked emoji item.
        """
        self.picked.emit(item)
        self.close()