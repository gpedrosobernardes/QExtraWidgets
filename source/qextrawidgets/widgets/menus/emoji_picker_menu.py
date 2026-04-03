import typing

from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QMenu, QWidgetAction, QWidget

from qextrawidgets.gui.items.icon_item import QIconItem
from qextrawidgets.gui.models import QIconPickerModel
from qextrawidgets.widgets.miscellaneous.emoji_picker import QEmojiPicker


class QEmojiPickerMenu(QMenu):
    """A menu that displays a QEmojiPicker.

    Signals:
        picked (QIconItem): Emitted when an emoji is selected.
    """

    picked = Signal(QIconItem)

    def __init__(
            self,
            parent: typing.Optional[QWidget] = None,
            model: typing.Optional[QIconPickerModel] = None,
            icon_label_size: int = 32,
            icon_pixmap_getter: typing.Optional[typing.Callable[[QIconItem], QPixmap]] = None) -> None:
        """Initialize the emoji picker menu.

        Args:
            parent (QWidget, optional): The parent widget.
            model (QEmojiPickerModel, optional): Custom emoji model. Defaults to None.
            icon_label_size (int): Size of the preview emoji label. Defaults to 32.
            icon_pixmap_getter (QIconItem[[str], QPixmap], optional):
                Method to generate emoji pixmaps. Defaults to EmojiImageProvider.getPixmap.
        """
        super().__init__(parent)
        self._picker = QEmojiPicker(parent, model, icon_label_size, icon_pixmap_getter)
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

    def _on_picked(self, item: QIconItem) -> None:
        """Handles the emoji picked signal.

        Args:
            item (QIconItem): The picked emoji item.
        """
        self.picked.emit(item)
        self.close()