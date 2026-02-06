import typing
from PySide6.QtWidgets import QLineEdit, QWidget

from qextrawidgets.gui.icons.theme_responsive_icon import QThemeResponsiveIcon


class QSearchLineEdit(QLineEdit):
    """A search line edit with a magnifying glass icon and a clear button."""

    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        """Initializes the search line edit.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setClearButtonEnabled(True)
        self.addAction(QThemeResponsiveIcon.fromAwesome("fa6s.magnifying-glass"), QLineEdit.ActionPosition.LeadingPosition)