import typing

import qtawesome
from PySide6.QtCore import QRect, Qt, QSize, QUrl, QUrlQuery
from PySide6.QtGui import QIcon, QIconEngine, QPainter, QPixmap, QPalette, QColor, QPixmapCache
from PySide6.QtWidgets import QApplication


class QThemeResponsiveIconEngine(QIconEngine):
    """
    Dynamic icon engine that acts as a Proxy for an original QIcon.
    Adjusts rendering based on the smallest available dimension to avoid clipping.
    """

    def __init__(self, icon: QIcon):
        super().__init__()
        self._source_icon = icon

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State):
        dpr = painter.device().devicePixelRatioF()

        pixmap = self._get_colored_pixmap(rect.size() * dpr, mode, state)
        pixmap.setDevicePixelRatio(dpr)

        if pixmap.isNull():
            return

        # Desenha o pixmap com tamanho explícito para garantir escala correta
        painter.drawPixmap(rect, pixmap)

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        """Returns processed pixmap."""
        return self._get_colored_pixmap(size, mode, state)

    def addPixmap(self, pixmap: QPixmap, mode: QIcon.Mode, state: QIcon.State):
        self._source_icon.addPixmap(pixmap, mode, state)

    def addFile(self, file_name: str, size: QSize, mode: QIcon.Mode, state: QIcon.State):
        self._source_icon.addFile(file_name, size, mode, state)

    def availableSizes(self, mode: QIcon.Mode = QIcon.Mode.Normal, state: QIcon.State = QIcon.State.Off) -> typing.List[QSize]:
        return self._source_icon.availableSizes(mode, state)

    def actualSize(self, size: QSize, mode: QIcon.Mode = QIcon.Mode.Normal, state: QIcon.State = QIcon.State.Off) -> QSize:
        return self._source_icon.actualSize(size, mode, state)

    def clone(self):
        return QThemeResponsiveIconEngine(self._source_icon)

    # --- Internal Logic ---

    def _get_colored_pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        # 1. Theme Color
        palette = QApplication.palette()
        if mode == QIcon.Mode.Disabled:
            target_color = palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText)
        else:
            target_color = palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText)

        # 2. Cache Check
        url = QUrl()
        url.setScheme("icons")
        url.setPath(str(id(self)))

        query_params = QUrlQuery()
        query_params.addQueryItem("width", str(size.width()))
        query_params.addQueryItem("height", str(size.height()))
        query_params.addQueryItem("mode", str(mode.value))
        query_params.addQueryItem("state", str(state.value))
        query_params.addQueryItem("color", str(target_color.rgba()))

        url.setQuery(query_params)

        base_pixmap = QPixmap()
        if QPixmapCache.find(url.toString(), base_pixmap):
            return base_pixmap

        # 3. Get Original Pixmap
        base_pixmap = self._source_icon.pixmap(size, mode, state)

        if base_pixmap.isNull():
            return QPixmap()

        # 4. Colorize
        colored_pixmap = self._generate_colored_pixmap(base_pixmap, target_color)

        QPixmapCache.insert(url.toString(), colored_pixmap)

        return colored_pixmap

    @staticmethod
    def _generate_colored_pixmap(base: QPixmap, color: QColor) -> QPixmap:
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
    """
    QIcon wrapper that applies automatic coloring based on system theme.
    The icon adjusts to the smallest available space maintaining aspect ratio.
    """
    def __init__(self, source: typing.Union[str, QPixmap, QIcon]):
        icon = QIcon()

        if isinstance(source, QIcon):
            icon = source
        elif isinstance(source, str):
            icon = QIcon(source)
        elif isinstance(source, QPixmap):
            icon = QIcon()
            icon.addPixmap(source)

        super().__init__(QThemeResponsiveIconEngine(icon))

    @staticmethod
    def fromAwesome(icon_name: str, **kwargs):
        return QThemeResponsiveIcon(qtawesome.icon(icon_name, **kwargs))
