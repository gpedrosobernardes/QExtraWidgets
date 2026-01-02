from emojis.db import Emoji
from twemoji_api.api import get_emoji_path
from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap, QPixmapCache, QImageReader, Qt


class EmojiImageProvider:
    """
    Classe responsável exclusivamente por carregar, dimensionar e cachear
    imagens de emojis.
    """

    @staticmethod
    def get_pixmap(emoji_data: Emoji, size: QSize, dpr: float = 1.0) -> QPixmap:
        """
        Retorna um QPixmap pronto para ser desenhado.

        :param emoji_data: Objeto contendo o caminho ou código do emoji.
        :param size: QSize desejado (tamanho lógico).
        :param dpr: Device Pixel Ratio (para telas Retina/4K).
        """

        # 1. Calcular tamanho físico real (pixels)
        target_width = int(size.width() * dpr)
        target_height = int(size.height() * dpr)

        # 2. Gerar chave única para o Cache
        # Ex: "emoji_1f600_64x64"
        emoji_alias = emoji_data[0][0]
        cache_key = f"emoji_{emoji_alias}"

        # 3. Tentar buscar no Cache
        pixmap = QPixmap()
        if QPixmapCache.find(cache_key, pixmap):
            return pixmap

        # --- CACHE MISS (Carregar do disco) ---

        # 4. Carregar usando QImageReader (mais eficiente que QPixmap(path))
        emoji_path = str(get_emoji_path(emoji_data[1]))
        reader = QImageReader(emoji_path)

        if reader.canRead():
            # Importante para SVG: Define o tamanho de renderização antes de ler
            reader.setScaledSize(QSize(target_width, target_height))

            image = reader.read()
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                pixmap.setDevicePixelRatio(dpr)

                # Salvar no cache para o futuro
                QPixmapCache.insert(cache_key, pixmap)
                return pixmap

        # 5. Fallback (Retorna um pixmap transparente ou placeholder em caso de erro)
        fallback = QPixmap(size * dpr)
        fallback.fill(Qt.GlobalColor.transparent)
        fallback.setDevicePixelRatio(dpr)
        return fallback