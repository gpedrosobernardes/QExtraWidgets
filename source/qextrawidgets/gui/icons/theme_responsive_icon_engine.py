import typing
from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QIconEngine, QIcon, QPainter, QPixmap, QColor, QImage
from PySide6.QtWidgets import QApplication


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
        self._theme_icons: typing.Dict[Qt.ColorScheme, QIcon] = {
            Qt.ColorScheme.Light: self._generate_colored_icon(icon, QColor(Qt.GlobalColor.black)),
            Qt.ColorScheme.Dark: self._generate_colored_icon(icon, QColor(Qt.GlobalColor.white)),
        }

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State) -> None:
        """Paints the icon.

        Args:
            painter (QPainter): The painter to use.
            rect (QRect): Target rectangle.
            mode (Mode): Icon mode.
            state (State): Icon state.
        """
        self.currentThemeIcon().paint(painter, rect, mode=mode, state=state)

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

    def addPixmap(self, pixmap: typing.Union[QPixmap, QImage], mode: QIcon.Mode, state: QIcon.State) -> None:
        """Adds a pixmap to the source icon.

        Args:
            pixmap (QPixmap | QImage): Pixmap to add.
            mode (Mode): Icon mode.
            state (State): Icon state.
        """
        if isinstance(pixmap, QImage):
            pixmap = QPixmap.fromImage(pixmap)

        self._source_icon.addPixmap(pixmap, mode, state)
        dark_icon = self._theme_icons[Qt.ColorScheme.Dark]
        dark_icon.addPixmap(self._generate_colored_pixmap(pixmap, QColor(Qt.GlobalColor.white)), mode, state)
        light_icon = self._theme_icons[Qt.ColorScheme.Light]
        light_icon.addPixmap(self._generate_colored_pixmap(pixmap, QColor(Qt.GlobalColor.black)), mode, state)

    def addFile(self, file_name: str, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> None:
        """Adds a file to the source icon.

        Args:
            file_name (str): Path to the icon file.
            size (QSize): Icon size.
            mode (Mode): Icon mode.
            state (State): Icon state.
        """
        pixmap = QPixmap(file_name)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.addPixmap(pixmap, mode, state)

    def availableSizes(self, mode: QIcon.Mode = QIcon.Mode.Normal, state: QIcon.State = QIcon.State.Off) -> typing.List[QSize]:
        """Returns available sizes for the icon.

        Args:
            mode (Mode, optional): Icon mode. Defaults to Normal.
            state (State, optional): Icon state. Defaults to Off.

        Returns:
            List[QSize]: List of available sizes.
        """
        return self.currentThemeIcon().availableSizes(mode, state)

    def actualSize(self, size: QSize, mode: QIcon.Mode = QIcon.Mode.Normal, state: QIcon.State = QIcon.State.Off) -> QSize:
        """Returns the actual size of the icon for the given parameters.

        Args:
            size (QSize): Requested size.
            mode (Mode, optional): Icon mode. Defaults to Normal.
            state (State, optional): Icon state. Defaults to Off.

        Returns:
            QSize: The actual size.
        """
        return self.currentThemeIcon().actualSize(size, mode, state)

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
        return self.themeIcon(scheme).pixmap(size, mode, state)

    def themeIcon(self, scheme: Qt.ColorScheme) -> QIcon:
        """Returns the icon associated with the given color scheme.

        Args:
            scheme (Qt.ColorScheme): The color scheme (Light or Dark).

        Returns:
            QIcon: The icon corresponding to the scheme.

        Raises:
            ValueError: If the scheme is unsupported.
        """
        if self._theme_icons.get(scheme) is None:
            raise ValueError(f"Unsupported color scheme: {scheme}")
        else:
            return self._theme_icons[scheme]

    def currentThemeIcon(self) -> QIcon:
        """Returns the icon for the current application theme.

        Returns:
            QIcon: The current theme icon.
        """
        return self.themeIcon(QApplication.styleHints().colorScheme())

    @staticmethod
    def _generate_colored_icon(base: QIcon, color: QColor) -> QIcon:
        """Applies a solid color to an icon mask.

        Args:
            base (QIcon): Source icon (used as mask).
            color (QColor): Target color.

        Returns:
            QIcon: The colorized icon.
        """
        colored = QIcon()
        for mode in QIcon.Mode:
            for state in QIcon.State:
                available_sizes = base.availableSizes(mode, state)
                if available_sizes:
                    pixmap = base.pixmap(max(available_sizes, key=lambda s: s.width() * s.height()), mode, state)
                else:
                    pixmap = base.pixmap(128, mode, state)

                if not pixmap.isNull():
                    colored.addPixmap(QThemeResponsiveIconEngine._generate_colored_pixmap(pixmap, color), mode, state)
        return colored

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
