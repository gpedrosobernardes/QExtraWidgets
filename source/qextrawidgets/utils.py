from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, QFontDatabase, QFontMetrics
from PySide6.QtWidgets import QApplication


def is_dark_mode() -> bool:
    style_hints = QApplication.styleHints()
    color_scheme = style_hints.colorScheme()
    return color_scheme.value == 2

def get_max_pixel_size(text: str, font_name: str, target_size: QSize):
    """
    Retorna o pixelSize máximo para que 'text' caiba inteiramente
    dentro de 'target_size' (width e height), mantendo a proporção.
    """
    if not text:
        return 12  # Tamanho fallback seguro

    # 1. Usamos um tamanho base arbitrário para fazer a medição inicial
    base_pixel_size = 100
    font = QFont(font_name)
    font.setPixelSize(base_pixel_size)

    fm = QFontMetrics(font)

    # 2. Obtemos as dimensões que o texto ocupa no tamanho base
    # horizontalAdvance: Largura total incluindo espaçamento natural da letra
    base_width = fm.horizontalAdvance(text)
    # height: Altura total da linha (Ascent + Descent).
    # É mais seguro que boundingRect().height() para evitar cortes em acentos/descidas.
    base_height = fm.height()

    if base_width == 0 or base_height == 0:
        return base_pixel_size

    # 3. Calculamos a razão de escala para cada dimensão
    # "Quantas vezes o meu texto base cabe dentro do alvo?"
    width_ratio = target_size.width() / base_width
    height_ratio = target_size.height() / base_height

    # 4. O Fator Limitante: Escolhemos o MENOR ratio.
    # Se o texto for largo (W), o width_ratio será menor e limitará o tamanho.
    # Se o texto for alto (I), o height_ratio será menor e limitará o tamanho.
    final_scale_factor = min(width_ratio, height_ratio)

    # 5. Aplicamos o fator ao tamanho base
    new_pixel_size = int(base_pixel_size * final_scale_factor)

    # Opcional: Trava de segurança para não retornar 0
    return max(1, new_pixel_size)

# https://github.com/googlefonts/color-fonts/tree/main/fonts


class QEmojiFonts:

    TwemojiFontFamily = None

    @classmethod
    def loadTwemojiFont(cls) -> str:

        if not cls.TwemojiFontFamily:
            root_folder_path = Path(__file__).parent
            fonts_folder_path = root_folder_path / "fonts"
            file_path = fonts_folder_path / "Twemoji-17.0.2.ttf"

            id_ = QFontDatabase.addApplicationFont(str(file_path))
            family = QFontDatabase.applicationFontFamilies(id_)[0]

            cls.TwemojiFontFamily = family

        return cls.TwemojiFontFamily

    @classmethod
    def twemojiFont(cls) -> QFont:
        return QFont(cls.loadTwemojiFont())