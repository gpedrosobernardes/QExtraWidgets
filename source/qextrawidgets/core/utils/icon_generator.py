from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QFont, QColor, QFontMetrics


class QIconGenerator:
    """Classe responsável por gerar Pixmaps e ícones baseados em texto/fontes."""

    @staticmethod
    def calculateMaxPixelSize(text: str, font: QFont, target_size: QSize) -> int:
        """
        Calcula o tamanho máximo (pixel size) que a fonte pode ter para que
        o texto caiba dentro de target_size.

        Args:
            text (str): Texto a ser medido.
            font (QFont): A configuração da fonte (família, peso, itálico).
            target_size (QSize): O espaço disponível.

        Returns:
            int: O pixel size calculado.
        """
        if not text:
            return 12  # tamanho de fallback seguro

        # 1. Trabalhamos com uma cópia para não alterar a fonte original fora daqui
        temp_font = QFont(font)

        # 2. Usamos um tamanho base arbitrário grande para precisão no cálculo
        base_pixel_size = 100
        temp_font.setPixelSize(base_pixel_size)

        fm = QFontMetrics(temp_font)

        # 3. Obter dimensões ocupadas pelo texto no tamanho base
        # horizontalAdvance: Largura total incluindo espaçamento natural
        base_width = fm.horizontalAdvance(text)
        # height: Altura total da linha (Ascent + Descent).
        base_height = fm.height()

        if base_width == 0 or base_height == 0:
            return base_pixel_size

        # 4. Calcular a razão de escala para cada dimensão
        width_ratio = target_size.width() / base_width
        height_ratio = target_size.height() / base_height

        # 5. O Fator Limitante é a MENOR razão (para garantir que caiba tanto na largura quanto altura)
        final_scale_factor = min(width_ratio, height_ratio)

        # 6. Aplicar fator ao tamanho base
        new_pixel_size = int(base_pixel_size * final_scale_factor)

        # Retorna pelo menos 1 para evitar erros de renderização
        return max(1, new_pixel_size)

    @classmethod
    def charToPixmap(
            cls,
            char: str,
            target_size: QSize,
            font: QFont = QFont("Arial"),
            color: QColor = Qt.GlobalColor.black
    ) -> QPixmap:
        """
        Gera um QPixmap de um tamanho específico contendo um caractere renderizado
        no maior tamanho possível.

        Args:
            char (str): O caractere a ser renderizado.
            target_size (QSize): O tamanho final da imagem (ex: 64x64).
            font (QFont): A fonte base (será redimensionada internamente).
            color (QColor): A cor do texto.

        Returns:
            QPixmap: Imagem transparente com o caractere centralizado.
        """
        if target_size.isEmpty():
            return QPixmap()

        # 1. Calcular o tamanho ideal da fonte para preencher o target_size
        optimal_size = cls.calculateMaxPixelSize(char, font, target_size)

        # 2. Configurar a fonte com o tamanho calculado
        render_font = QFont(font)
        render_font.setPixelSize(optimal_size)

        # 3. Criar o Pixmap com o tamanho exato solicitado
        pixmap = QPixmap(target_size)
        pixmap.fill(Qt.GlobalColor.transparent)

        # 4. Configurar o Painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setFont(render_font)
        painter.setPen(color)

        # 5. Desenhar o texto centralizado no retângulo do Pixmap
        # O Qt.AlignCenter cuida do posicionamento X e Y automaticamente
        rect = pixmap.rect()
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, char)

        painter.end()

        return pixmap