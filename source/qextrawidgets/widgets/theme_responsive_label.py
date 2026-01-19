from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QResizeEvent
from PySide6.QtWidgets import QLabel, QApplication, QWidget

from qextrawidgets.icons import QThemeResponsiveIcon


class QThemeResponsiveLabel(QLabel):
    """
    A QLabel that displays a QThemeResponsiveIcon and updates it automatically
    when the system theme or the widget size changes.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initializes the label.

        Args:
            parent: The parent widget.
        """
        super().__init__(parent)
        self._icon: Optional[QThemeResponsiveIcon] = None
        style_hints = QApplication.styleHints()
        style_hints.colorSchemeChanged.connect(self._on_theme_change)

    def _on_theme_change(self, scheme: Qt.ColorScheme) -> None:
        """
        Handles theme change events.
        """
        self._update_pixmap(scheme)

    def _update_pixmap(self, scheme: Qt.ColorScheme) -> None:
        """
        Updates the label's pixmap based on the current icon and size.
        """
        if self._icon:
            size = self.size()
            if not size.isEmpty():
                pixmap = self._icon.themePixmap(size, QIcon.Mode.Normal, QIcon.State.Off, scheme)
                self.setPixmap(pixmap)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Updates the pixmap when the widget is resized.

        Args:
            event: The resize event.
        """
        super().resizeEvent(event)
        self._update_pixmap(QApplication.styleHints().colorScheme())

    def setIcon(self, icon: QThemeResponsiveIcon) -> None:
        """
        Sets the icon to be displayed.

        Args:
            icon: The theme-responsive icon.
        """
        self._icon = icon
        self._update_pixmap(QApplication.styleHints().colorScheme())

    def icon(self) -> Optional[QThemeResponsiveIcon]:
        """
        Returns the current icon.

        Returns:
            The current icon or None.
        """
        return self._icon
