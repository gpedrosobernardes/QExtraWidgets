import typing
from PySide6.QtCore import QIdentityProxyModel, Qt, QObject


class QHeaderProxyModel(QIdentityProxyModel):
    """A proxy model that handles header data customizations, such as icons."""

    def __init__(self, parent: typing.Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._header_icons = {}

    def setHeaderData(
        self,
        section: int,
        orientation: Qt.Orientation,
        value: typing.Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        """Sets the header data for the given section and orientation."""
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DecorationRole
        ):
            self._header_icons[section] = value
            self.headerDataChanged.emit(orientation, section, section)
            return True
        return super().setHeaderData(section, orientation, value, role)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> typing.Any:
        """Returns the header data for the given section and orientation."""
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DecorationRole
        ):
            if section in self._header_icons:
                return self._header_icons[section]
        return super().headerData(section, orientation, role)

    def reset(self):
        """Resets the header icons."""
        self._header_icons = {}
        # We might need to emit layoutChanged or headerDataChanged if we were clearing extensive state,
        # but here we rely on the caller to manage refreshing if needed, or we just leave it as is
        # until the next setHeaderData update. However, if we clear icons, we should probably signal it.
        # But for now, let's just clear the dict. The table view usually triggers a full refresh anyway.
