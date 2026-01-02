from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle

from extra_qwidgets.widgets.emoji_picker.emoji_image_provider import EmojiImageProvider


class EmojiDelegate(QStyledItemDelegate):
    """
    Renderiza o Emoji. Se for uma imagem, desenha o Pixmap.
    Se for fonte, desenha o texto. Isso economiza memória em comparação a criar QIcons.
    """

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        if not index.isValid():
            return

        painter.save()

        state = getattr(option, "state")
        rect = getattr(option, "rect")
        palette = getattr(option, "palette")

        # 1. Desenhar o fundo (hover/seleção)
        if state & QStyle.StateFlag.State_Selected:
            painter.fillRect(rect, palette.highlight())
        elif state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(rect, palette.midlight())

        # 2. Obter dados do Emoji
        # Assumindo que você guardou o caminho do arquivo ou o código no UserRole
        emoji_data = index.data(Qt.ItemDataRole.UserRole)

        # 3. Definir o retângulo onde o ícone será desenhado (com padding)
        icon_rect = getattr(option, "rect")
        icon_rect_adjusted = icon_rect.adjusted(4, 4, -4, -4)

        pixmap = EmojiImageProvider.get_pixmap(
            emoji_data,
            icon_rect_adjusted.size(),
            painter.device().devicePixelRatio()
        )

        # 4. Desenhar
        if not pixmap.isNull():
            # Centralizar
            # Como o pixmap tem devicePixelRatio configurado, usamos as dimensões lógicas (divididas por dpr) para alinhar
            logical_w = pixmap.width() / pixmap.devicePixelRatio()
            logical_h = pixmap.height() / pixmap.devicePixelRatio()

            x = icon_rect_adjusted.x() + (icon_rect_adjusted.width() - logical_w) / 2
            y = icon_rect_adjusted.y() + (icon_rect_adjusted.height() - logical_h) / 2

            painter.drawPixmap(int(x), int(y), pixmap)

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(40, 40)  # Tamanho fixo para performance
