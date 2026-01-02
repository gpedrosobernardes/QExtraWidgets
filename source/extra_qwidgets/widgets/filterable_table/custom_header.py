from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPainter, QIcon
from PySide6.QtWidgets import QHeaderView, QStyle, QStyleOptionHeader


class CustomHeader(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)
        # Opcional: Permite que o texto tenha "..." se for muito longo
        self.setTextElideMode(Qt.TextElideMode.ElideRight)

    def paintSection(self, painter: QPainter, rect: QRect, logicalIndex):
        painter.save()

        # 1. Configura as opções de estilo nativo
        opt = QStyleOptionHeader()
        self.initStyleOption(opt)
        opt.rect = rect
        opt.section = logicalIndex
        opt.textAlignment = Qt.AlignmentFlag.AlignCenter

        # Obtém dados do modelo
        model = self.model()
        if model:
            # Texto
            text = model.headerData(logicalIndex, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            opt.text = str(text) if text is not None else ""

            # Alinhamento
            alignment = model.headerData(logicalIndex, Qt.Orientation.Horizontal, Qt.ItemDataRole.TextAlignmentRole)
            if alignment:
                opt.textAlignment = alignment

            # Ícone (Filtro)
            icon = model.headerData(logicalIndex, Qt.Orientation.Horizontal, Qt.ItemDataRole.DecorationRole)

            # 2. Lógica de Desenho

            # Margem para o ícone (se houver)
            icon_size = 16  # Tamanho padrão confortável
            padding = 4

            # Se tiver ícone, reservamos espaço na direita para ele
            # para que o texto nativo não desenhe em cima dele
            if isinstance(icon, QIcon) and not icon.isNull():
                # Reduz a área onde o Qt pode desenhar o texto/fundo
                # para não cobrir o nosso ícone customizado na direita
                # Nota: Dependendo do estilo, pode ser melhor desenhar o fundo primeiro (control)
                # e depois desenhar o ícone e texto manualmente se quiser controle total.

                # Vamos desenhar o controle nativo (Fundo + Texto)
                # Mas vamos enganar o style dizendo que não tem ícone, pois vamos desenhar manualmente na direita
                opt.icon = QIcon()
                self.style().drawControl(QStyle.ControlElement.CE_Header, opt, painter, self)

                # Desenha o ícone alinhado à direita manualmente
                icon_rect = QRect(
                    rect.right() - icon_size - padding,
                    rect.top() + (rect.height() - icon_size) // 2,
                    icon_size,
                    icon_size
                )

                # Estado do ícone (ativo/disabled) baseado no header
                mode = QIcon.Mode.Normal
                if not self.isEnabled():
                    mode = QIcon.Mode.Disabled
                elif opt.state & QStyle.State_MouseOver:
                    mode = QIcon.Mode.Active

                icon.paint(painter, icon_rect, alignment=Qt.AlignmentFlag.AlignCenter, mode=mode)

            else:
                # Desenho padrão nativo completo
                self.style().drawControl(QStyle.ControlElement.CE_Header, opt, painter, self)

        painter.restore()