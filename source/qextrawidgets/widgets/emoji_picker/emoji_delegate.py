import typing

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QPixmap, QIcon
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle, QApplication

from qextrawidgets.emoji_utils import EmojiImageProvider


class QLazyLoadingEmojiDelegate(QStyledItemDelegate):
    """
    Renders the Emoji. If it's an image, draws the Pixmap.
    If it's font, draws the text. This saves memory compared to creating QIcons.
    """
    def __init__(self):
        super().__init__()
        self.__emoji_image_getter = lambda emoji, size, dpr: EmojiImageProvider.getPixmap(emoji, 0, size, dpr, "png")

    def initStyleOption(self, option: QStyleOptionViewItem, index):
        super().initStyleOption(option, index)
        
        # 1. Centralizar o retângulo de desenho com base no decorationSize
        # Isso garante que a seleção, o hover e o foco tenham o tamanho correto.
        box_size = option.decorationSize
        if box_size.isValid() and not option.rect.isEmpty():
            option.rect = QStyle.alignedRect(
                option.direction,
                Qt.AlignmentFlag.AlignCenter,
                box_size,
                option.rect
            )

        # 2. Limpar texto e ícone para desenho manual
        option.text = ""
        option.icon = QIcon()
        
        # 3. Remover flags que forçam o estilo a desenhar elementos que faremos manualmente
        option.features &= ~(QStyleOptionViewItem.ViewItemFeature.HasDisplay | 
                             QStyleOptionViewItem.ViewItemFeature.HasDecoration)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        if not index.isValid():
            return

        painter.save()

        # Preparar as opções de estilo usando a lógica centralizada
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        # Obter o estilo e o widget
        widget = opt.widget
        style = widget.style() if widget else QApplication.style()

        # Desenhar Background, Seleção, Hover e Foco
        # O uso de ClipRect ainda é recomendado para forçar estilos teimosos (como Windows)
        painter.save()
        painter.setClipRect(opt.rect)
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, widget)
        painter.restore()

        # Desenhar o Emoji com margem de 10%
        emoji = index.data(Qt.ItemDataRole.DisplayRole)
        if emoji:
            box_rect = opt.rect
            margin_x = box_rect.width() * 0.1
            margin_y = box_rect.height() * 0.1
            emoji_rect = box_rect.adjusted(margin_x, margin_y, -margin_x, -margin_y)
            
            dpr = painter.device().devicePixelRatio()
            pixmap = self.__emoji_image_getter(emoji, emoji_rect.size(), dpr)
            
            if not pixmap.isNull():
                target_rect = QStyle.alignedRect(
                    Qt.LayoutDirection.LeftToRight,
                    Qt.AlignmentFlag.AlignCenter,
                    pixmap.size(),
                    emoji_rect
                )
                painter.drawPixmap(target_rect, pixmap)

        painter.restore()

    def setEmojiImageGetter(self, func: typing.Callable[[str, QSize, float], QPixmap]):
        self.__emoji_image_getter = func

    def emojiImageGetter(self) -> typing.Callable[[str, QSize, float], QPixmap]:
        return self.__emoji_image_getter

    def sizeHint(self, option: QStyleOptionViewItem, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        return opt.rect.size()
