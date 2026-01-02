import typing

import qtawesome
from PySide6.QtCore import QRect, Qt, QSize, QPoint
from PySide6.QtGui import QIcon, QIconEngine, QPainter, QPixmap, QPalette, QColor, QGuiApplication
from PySide6.QtWidgets import QApplication


class AutoThemeIconEngine(QIconEngine):
    def __init__(self, pixmap: QPixmap):
        super().__init__()
        self._base_pixmap = pixmap

        # Variáveis de Cache
        self._cached_pixmap: typing.Optional[QPixmap] = None
        self._last_color_key: typing.Optional[int] = None
        self._last_mode: typing.Optional[QIcon.Mode] = None

    # --- MÉTODO CENTRAL DE LÓGICA ---
    def _get_colored_pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        """
        Gera ou recupera do cache o pixmap colorido correto para o estado atual.
        Este método é usado tanto pelo paint() quanto pelo pixmap().
        """
        if self._base_pixmap.isNull():
            return QPixmap()

        # 1. Determina a cor alvo (Active/Disabled/etc)
        # Como não temos o 'painter' aqui, usamos a QApplication como fallback principal
        # Se quiséssemos ser precisos com o widget pai, precisaríamos passá-lo,
        # mas QIconEngine não tem acesso fácil ao widget proprietário no método pixmap().
        # Usar QApplication.palette() é o padrão para "seguir o tema do Windows".
        palette = QApplication.palette()

        if mode == QIcon.Mode.Disabled:
            target_color = palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText)
        else:
            target_color = palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText)

        # 2. Verifica Cache
        current_color_key = target_color.rgba()

        # O cache precisa considerar o tamanho solicitado também, senão ícones pequenos ficam borrados
        # se o cache tiver uma imagem grande (ou vice-versa)
        if (self._cached_pixmap and
                self._cached_pixmap.size() == size and
                self._last_color_key == current_color_key and
                self._last_mode == mode):
            return self._cached_pixmap

        # 3. Gera Nova Imagem Colorida
        # Redimensiona a base primeiro para o tamanho desejado (Melhor qualidade)
        scaled_base = self._base_pixmap.scaled(
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        colored_pixmap = QPixmap(scaled_base.size())
        colored_pixmap.fill(Qt.GlobalColor.transparent)

        p = QPainter(colored_pixmap)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Pinta a cor
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        p.fillRect(colored_pixmap.rect(), target_color)

        # Aplica a máscara (SourceIn mantém a cor onde a imagem existe)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        p.drawPixmap(0, 0, scaled_base)
        p.end()

        # Atualiza cache
        self._cached_pixmap = colored_pixmap
        self._last_color_key = current_color_key
        self._last_mode = mode

        return colored_pixmap

    # --- OVERRIDES OBRIGATÓRIOS DO QT ---

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State):
        """
        Chamado quando o widget desenha diretamente (ex: alguns Delegates).
        """
        # Pega a imagem colorida já no tamanho final do rect
        pixmap = self._get_colored_pixmap(rect.size(), mode, state)

        # Centraliza e desenha
        target_rect = QRect(QPoint(0, 0), pixmap.size())
        target_rect.moveCenter(rect.center())

        painter.drawPixmap(target_rect, pixmap)

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        """
        Chamado pelo QToolButton e QIcon::pixmap().
        AQUI estava o erro: antes retornávamos a imagem sem cor.
        """
        return self._get_colored_pixmap(size, mode, state)

    def clone(self):
        return AutoThemeIconEngine(self._base_pixmap)


class QThemeResponsiveIcon(QIcon):
    def __init__(self, source: typing.Union[str, QPixmap, QIcon], size: int = 64):
        pixmap = QPixmap()
        if isinstance(source, str):
            pixmap = QPixmap(source)
        elif isinstance(source, QIcon):
            pixmap = source.pixmap(QSize(size, size))
        elif isinstance(source, QPixmap):
            pixmap = source
        super().__init__(AutoThemeIconEngine(pixmap))

    @staticmethod
    def fromAwesome(icon_name: str, size: int = 64, **kwargs):
        # Usamos white/black apenas para gerar a forma, a cor real será sobreposta
        return QThemeResponsiveIcon(qtawesome.icon(icon_name, **kwargs), size)