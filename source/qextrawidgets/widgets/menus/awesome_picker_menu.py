import typing

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMenu, QWidgetAction, QWidget

from qextrawidgets.gui.items.icon_item import QIconItem
from qextrawidgets.gui.models import QIconPickerModel
from qextrawidgets.widgets.miscellaneous.awesome_picker import QAwesomePicker


class QAwesomePickerMenu(QMenu):
    """A menu that displays a QEmojiPicker.

    Signals:
        picked (str): Emitted when an emoji is selected.
    """

    picked = Signal(QIconItem)

    def __init__(
            self,
            parent: typing.Optional[QWidget] = None,
            model: typing.Optional[QIconPickerModel] = None,
            icon_label_size: int = 32) -> None:
        """Initialize the emoji picker menu.

        Args:
            parent (QWidget, optional): The parent widget.
            model (QEmojiPickerModel, optional): Custom emoji model. Defaults to None.
            emoji_pixmap_getter (Union[str, QFont, Callable[[str], QPixmap]], optional):
                Method or font to generate emoji pixmaps. Defaults to EmojiImageProvider.getPixmap.
            emoji_label_size (QSize, optional): Size of the preview emoji label. Defaults to QSize(32, 32).
        """
        super().__init__(parent)
        self._picker = QAwesomePicker(parent, model, icon_label_size)
        self._picker.picked.connect(self._on_picked)

        action = QWidgetAction(self)
        action.setDefaultWidget(self._picker)
        self.addAction(action)

    def picker(self) -> QAwesomePicker:
        """Returns the internal emoji picker widget.

        Returns:
            QAwesomePickerMenu: The emoji picker widget.
        """
        return self._picker

    def _on_picked(self, item: QIconItem) -> None:
        """Handles the emoji picked signal.

        Args:
            item (QIconItem): The picked emoji item.
        """
        self.picked.emit(item)
        self.close()