import typing

import qtawesome
from PySide6.QtCore import QRect, Qt, QSize, QUrl, QUrlQuery
from PySide6.QtGui import QIcon, QIconEngine, QPainter, QPixmap, QPalette, QColor, QPixmapCache
from PySide6.QtWidgets import QApplication, QStyle


class QThemeResponsiveIconEngine(QIconEngine):
    """Dynamic icon engine that acts as a proxy for an original QIcon.

    Adjusts rendering based on the system theme (Black/White) and ensures
    the icon fits within the requested dimensions without clipping.
    """

    def __init__(self, icon: QIcon) -> None:
        """Initializes the icon engine.

        Args:
            icon (QIcon): The source icon to be colorized.
        """
        super().__init__()
        self._source_icon = icon

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State) -> None:
        """Paints the icon.

        Args:
            painter (QPainter): The painter to use.
            rect (QRect): Target rectangle.
            mode (Mode): Icon mode.
            state (State): Icon state.
        """
        dpr = painter.device().devicePixelRatioF()

        min_side = min(rect.width(), rect.height())
        size = QSize(min_side, min_side)

        pixmap = self.themePixmap(size * dpr, mode, state, QApplication.styleHints().colorScheme())

        if pixmap.isNull():
            return

        # Fix: Calculate exact device pixel ratio to avoid scaling artifacts due to rounding
        if size.width() > 0:
            physical_width = pixmap.width() * pixmap.devicePixelRatio()
            pixmap.setDevicePixelRatio(physical_width / size.width())
        else:
            pixmap.setDevicePixelRatio(dpr)

        target_rect = QStyle.alignedRect(
            Qt.LayoutDirection.LeftToRight,  # layout direction (LTR)
            Qt.AlignmentFlag.AlignCenter,  # desired alignment
            size,  # object size
            rect  # bounding rectangle
        )

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.drawPixmap(target_rect, pixmap)
        painter.restore()

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        """Returns processed pixmap.

        Args:
            size (QSize): Requested size.
            mode (Mode): Icon mode.
            state (State): Icon state.

        Returns:
            QPixmap: The colorized pixmap.
        """
        return self.themePixmap(size, mode, state, QApplication.styleHints().colorScheme())

    def addPixmap(self, pixmap: QPixmap, mode: QIcon.Mode, state: QIcon.State) -> None:
        """Adds a pixmap to the source icon.

        Args:
            pixmap (QPixmap): Pixmap to add.
            mode (Mode): Icon mode.
            state (State): Icon state.
        """
        self._source_icon.addPixmap(pixmap, mode, state)

    def addFile(self, file_name: str, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> None:
        """Adds a file to the source icon.

        Args:
            file_name (str): Path to the icon file.
            size (QSize): Icon size.
            mode (Mode): Icon mode.
            state (State): Icon state.
        """
        self._source_icon.addFile(file_name, size, mode, state)

    def availableSizes(self, mode: QIcon.Mode = QIcon.Mode.Normal, state: QIcon.State = QIcon.State.Off) -> typing.List[QSize]:
        """Returns available sizes for the icon.

        Args:
            mode (Mode, optional): Icon mode. Defaults to Normal.
            state (State, optional): Icon state. Defaults to Off.

        Returns:
            List[QSize]: List of available sizes.
        """
        return self._source_icon.availableSizes(mode, state)

    def actualSize(self, size: QSize, mode: QIcon.Mode = QIcon.Mode.Normal, state: QIcon.State = QIcon.State.Off) -> QSize:
        """Returns the actual size of the icon for the given parameters.

        Args:
            size (QSize): Requested size.
            mode (Mode, optional): Icon mode. Defaults to Normal.
            state (State, optional): Icon state. Defaults to Off.

        Returns:
            QSize: The actual size.
        """
        return self._source_icon.actualSize(size, mode, state)

    def clone(self) -> "QThemeResponsiveIconEngine":
        """Returns a clone of this engine.

        Returns:
            QThemeResponsiveIconEngine: The cloned engine.
        """
        return QThemeResponsiveIconEngine(self._source_icon)

    # --- Internal Logic ---

    def themePixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State, scheme: Qt.ColorScheme) -> QPixmap:
        """Generates a colorized pixmap based on the current theme scheme.

        Args:
            size (QSize): Target size.
            mode (Mode): Icon mode.
            state (State): Icon state.
            scheme (ColorScheme): System color scheme (Light/Dark).

        Returns:
            QPixmap: The themed pixmap.
        """
        # 1. Theme Color
        target_color = Qt.GlobalColor.white if scheme == Qt.ColorScheme.Dark else Qt.GlobalColor.black

        # 3. Get Original Pixmap
        base_pixmap = self._source_icon.pixmap(size, mode, state)

        # 4. Colorize
        colored_pixmap = self._generate_colored_pixmap(base_pixmap, target_color)

        return colored_pixmap

    @staticmethod
    def _generate_colored_pixmap(base: QPixmap, color: QColor) -> QPixmap:
        """Applies a solid color to a pixmap mask.

        Args:
            base (QPixmap): Source pixmap (used as mask).
            color (QColor): Target color.

        Returns:
            QPixmap: Colorized pixmap.
        """
        colored = QPixmap(base.size())
        colored.fill(Qt.GlobalColor.transparent)
        colored.setDevicePixelRatio(base.devicePixelRatio())

        p = QPainter(colored)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Paint color
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        p.fillRect(colored.rect(), color)

        # Cut shape
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        p.drawPixmap(0, 0, base)
        p.end()

        return colored


class QThemeResponsiveIcon(QIcon):
    """QIcon wrapper that applies automatic coloring based on system theme.

    The icon switches between Black and White based on the current system palette.
    """

    def __init__(self, source: typing.Union[str, QPixmap, QIcon] = None) -> None:
        """Initializes the theme responsive icon.

        Args:
            source (Union[str, QPixmap, QIcon], optional): Icon source. Defaults to None.
        """
        if isinstance(source, QIcon):
            icon = source
        elif isinstance(source, str):
            icon = QIcon(source)
        elif isinstance(source, QPixmap):
            icon = QIcon()
            icon.addPixmap(source)
        else:
            icon = QIcon()

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
