import typing

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMenu, QWidgetAction, QWidget

from qextrawidgets.gui.items.icon_item import QIconItem
from qextrawidgets.gui.models import QIconPickerModel
from qextrawidgets.widgets.miscellaneous.awesome_picker import QAwesomePicker


class QAwesomePickerMenu(QMenu):
    """A menu that displays a QAwesomePicker.

    Signals:
        picked (QIconItem): Emitted when an icon is selected.
    """

    picked = Signal(QIconItem)

    def __init__(
            self,
            parent: typing.Optional[QWidget] = None,
            model: typing.Optional[QIconPickerModel] = None,
            icon_label_size: int = 32) -> None:
        """Initialize the qt awesome icon picker menu.

        Args:
            parent (QWidget, optional): The parent widget.
            model (QIconPickerModel, optional): Different icon model. Defaults to None.
            icon_label_size (int): Size of the preview icon label. Defaults to 32.
        """
        super().__init__(parent)
        self._picker = QAwesomePicker(parent, model, icon_label_size)
        self._picker.picked.connect(self._on_picked)

        action = QWidgetAction(self)
        action.setDefaultWidget(self._picker)
        self.addAction(action)

    def picker(self) -> QAwesomePicker:
        """Returns the internal qt awesome picker widget.

        Returns:
            QAwesomePickerMenu: The qt awesome picker widget.
        """
        return self._picker

    def _on_picked(self, item: QIconItem) -> None:
        """Handles the emoji picked signal.

        Args:
            item (QIconItem): The picked icon item.
        """
        self.picked.emit(item)
        self.close()