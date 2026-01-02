import typing

import qtawesome
from PySide6.QtCore import QRect, Qt, QSize, QPoint
from PySide6.QtGui import QIcon, QIconEngine, QPainter, QPixmap, QPalette, QColor
from PySide6.QtWidgets import QApplication


class ThemeResponsiveIconEngine(QIconEngine):
    """
    Motor de ícone dinâmico que atua como Proxy para um QIcon original.
    Ajusta a renderização baseada na menor dimensão disponível para evitar cortes.
    """

    def __init__(self, icon: QIcon):
        super().__init__()
        self._source_icon = icon

        # Cache simples
        self._cached_pixmap: typing.Optional[QPixmap] = None
        self._cache_key: typing.Optional[tuple] = None  # (width, height, mode, state, color_rgba)

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State):
        """
        Pinta o ícone centralizado, limitado pela menor dimensão do retângulo.
        """
        # 1. Determina o tamanho do quadrado delimitador (bounding box)
        min_side = min(rect.width(), rect.height())

        # Margem de segurança (2px cada lado) para evitar cortes de anti-aliasing
        safe_side = min_side - 4

        if safe_side <= 0:
            return

        bounding_size = QSize(safe_side, safe_side)

        # 2. Obter o Pixmap Colorido
        # Solicitamos o pixmap com base nesse tamanho delimitador
        pixmap = self._getColoredPixmap(bounding_size, mode, state)

        if pixmap.isNull():
            return

        # 3. Cálculo de Escala (Mantendo Aspect Ratio)
        pixmap_size = pixmap.size()

        # CORREÇÃO AQUI: QSize.scaled aceita apenas (Size, Mode).
        # A suavização visual é feita pelo painter.setRenderHint posteriormente.
        scaled_size = pixmap_size.scaled(
            bounding_size,
            Qt.AspectRatioMode.KeepAspectRatio
        )

        # 4. Centralização
        # Calcula a posição (x, y) para centralizar no rect original
        x = rect.x() + (rect.width() - scaled_size.width()) // 2
        y = rect.y() + (rect.height() - scaled_size.height()) // 2

        target_rect = QRect(x, y, scaled_size.width(), scaled_size.height())

        # 5. Desenho
        # Ativa a suavização na hora de desenhar os pixels na tela
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.drawPixmap(target_rect, pixmap)

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        """Retorna o pixmap processado."""
        return self._getColoredPixmap(size, mode, state)

    def addPixmap(self, pixmap: QPixmap, mode: QIcon.Mode, state: QIcon.State):
        self._source_icon.addPixmap(pixmap, mode, state)
        self._clearCache()

    def addFile(self, fileName: str, size: QSize, mode: QIcon.Mode, state: QIcon.State):
        self._source_icon.addFile(fileName, size, mode, state)
        self._clearCache()

    def availableSizes(self, mode: QIcon.Mode = QIcon.Mode.Normal, state: QIcon.State = QIcon.State.Off) -> typing.List[QSize]:
        return self._source_icon.availableSizes(mode, state)

    def actualSize(self, size: QSize, mode: QIcon.Mode = QIcon.Mode.Normal, state: QIcon.State = QIcon.State.Off) -> QSize:
        return self._source_icon.actualSize(size, mode, state)

    def clone(self):
        return ThemeResponsiveIconEngine(self._source_icon)

    # --- Lógica Interna ---

    def _getColoredPixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        # 1. Cor do Tema
        palette = QApplication.palette()
        if mode == QIcon.Mode.Disabled:
            target_color = palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText)
        else:
            target_color = palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText)

        # 2. Verificação de Cache
        current_key = (size.width(), size.height(), mode, state, target_color.rgba())

        if self._cached_pixmap and self._cache_key == current_key:
            return self._cached_pixmap

        # 3. Obter Pixmap Original
        base_pixmap = self._source_icon.pixmap(size, mode, state)

        if base_pixmap.isNull():
            return QPixmap()

        # 4. Colorir
        colored_pixmap = self._generateColoredPixmap(base_pixmap, target_color)

        # Atualizar Cache
        self._cached_pixmap = colored_pixmap
        self._cache_key = current_key

        return colored_pixmap

    def _generateColoredPixmap(self, base: QPixmap, color: QColor) -> QPixmap:
        colored = QPixmap(base.size())
        colored.fill(Qt.GlobalColor.transparent)

        p = QPainter(colored)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Pinta cor
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        p.fillRect(colored.rect(), color)

        # Recorta forma
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        p.drawPixmap(0, 0, base)
        p.end()

        return colored

    def _clearCache(self):
        self._cached_pixmap = None
        self._cache_key = None


class QThemeResponsiveIcon(QIcon):
    """
    Wrapper de QIcon que aplica coloração automática baseada no tema do sistema.
    O ícone se ajusta ao menor espaço disponível mantendo o aspect ratio.
    """
    def __init__(self, source: typing.Union[str, QPixmap, QIcon], size: int = 64):
        icon = QIcon()

        if isinstance(source, QIcon):
            icon = source
        elif isinstance(source, str):
            icon = QIcon(source)
        elif isinstance(source, QPixmap):
            icon = QIcon()
            icon.addPixmap(source)

        super().__init__(ThemeResponsiveIconEngine(icon))

    @staticmethod
    def fromAwesome(icon_name: str, size: int = 64, **kwargs):
        return QThemeResponsiveIcon(qtawesome.icon(icon_name, **kwargs), size)