import typing

import qtawesome
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap

from qextrawidgets.gui.icons.theme_responsive_icon_engine import QThemeResponsiveIconEngine


class QThemeResponsiveIcon(QIcon):
    """QIcon wrapper that applies automatic coloring based on system theme.

    The icon switches between Black and White based on the current system palette.
    """

    def __init__(self, source: typing.Union[str, QPixmap, QIcon, None] = None) -> None:
        """Initializes the theme responsive icon.

        Args:
            source (Union[str, QPixmap, QIcon, None]): Icon source.
        """
        if isinstance(source, QIcon):
            icon = source
        elif isinstance(source, str):
            icon = QIcon(source)
        elif isinstance(source, QPixmap):
            icon = QIcon()
            icon.addPixmap(source)
        elif source is None:
            icon = QIcon()
        else:
            raise ValueError("Invalid source type")

        self._engine = QThemeResponsiveIconEngine(icon)

        super().__init__(self._engine)

    @staticmethod
    def fromAwesome(icon_name: str, **kwargs: typing.Any) -> "QThemeResponsiveIcon":
        """Creates a theme responsive icon from a QtAwesome icon name.

        Args:
            icon_name (str): QtAwesome icon name (e.g., "fa6s.house").
            **kwargs (Any): Additional arguments for qtawesome.icon.

        Returns:
            QThemeResponsiveIcon: The created icon.
        """
        return QThemeResponsiveIcon(qtawesome.icon(icon_name, **kwargs))

    def themePixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State, scheme: Qt.ColorScheme) -> QPixmap:
        """Returns a themed pixmap directly.

        Args:
            size (QSize): Target size.
            mode (Mode): Icon mode.
            state (State): Icon state.
            scheme (ColorScheme): System color scheme.

        Returns:
            QPixmap: The themed pixmap.
        """
        return self._engine.themePixmap(size, mode, state, scheme)
