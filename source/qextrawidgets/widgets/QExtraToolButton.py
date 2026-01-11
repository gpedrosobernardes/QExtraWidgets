from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QToolButton, QStyleOptionToolButton, QStyle


class QExtraToolButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._force_hover = False

    def setForceHover(self, enable: bool):
        self._force_hover = enable
        self.update() # Força redesenho imediato

    def paintEvent(self, event):
        # Cria as opções de estilo padrão
        opt = QStyleOptionToolButton()
        self.initStyleOption(opt)

        # O TRUQUE: Injetamos o estado de MouseOver se a flag estiver ativa
        if self._force_hover:
            opt.state |= QStyle.StateFlag.State_MouseOver
            opt.state |= QStyle.StateFlag.State_Enabled # Garante que pareça habilitado

        # Manda o estilo desenhar o botão com nossas opções falsificadas
        painter = QPainter(self)
        self.style().drawComplexControl(QStyle.ComplexControl.CC_ToolButton, opt, painter, self)