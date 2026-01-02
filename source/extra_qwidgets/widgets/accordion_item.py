from enum import IntEnum, auto

from PySide6.QtCore import Signal, QSize
from PySide6.QtGui import Qt, QMouseEvent
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QFrame, QSizePolicy, QVBoxLayout, QToolButton, QLineEdit

from extra_qwidgets.icons import QThemeResponsiveIcon


# Certifique-se de que o arquivo icons.py está no mesmo diretório ou ajuste a importação



class QAccordionHeader(QFrame):
    clicked = Signal()

    IconPosition = QLineEdit.ActionPosition

    class IndicatorStyle(IntEnum):
        Arrow = auto()  # Seta (> v)
        PlusMinus = auto()  # Mais/Menos (+ -)

    def __init__(self, title="", parent=None):
        super().__init__(parent)

        # Estilo visual nativo
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        # Estados
        self._is_expanded = False
        self._icon_position = QAccordionHeader.IconPosition.LeadingPosition
        self._icon_style = QAccordionHeader.IndicatorStyle.Arrow

        # Widgets
        self._label_title = QLabel(title)
        self._label_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # --- MUDANÇA: Usamos QToolButton em vez de QLabel ---
        # Isso permite que o QAutoIcon gerencie a pintura dinâmica (cores)
        self._btn_icon = QToolButton()
        self._btn_icon.setFixedSize(24, 24)
        self._btn_icon.setIconSize(QSize(16, 16))  # Tamanho do desenho do ícone
        self._btn_icon.setAutoRaise(True)  # Remove bordas de botão

        # Importante: O botão deve ignorar o mouse para que o clique
        # seja capturado pelo Header (QFrame) e não "roubado" pelo botão.
        self._btn_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Layout
        self._layout_header = QHBoxLayout(self)
        self._layout_header.setContentsMargins(10, 5, 10, 5)

        # Inicialização
        self.updateIcon()
        self.refreshLayout()
        self.setFlat(False)

    def setFlat(self, flat: bool):
        """
        Define se o header parece um botão elevado (False) ou texto plano (True).
        """
        if flat:
            self.setFrameStyle(QFrame.Shape.NoFrame)
            self.setAutoFillBackground(False)
        else:
            self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
            self.setAutoFillBackground(True)

    def flat(self) -> bool:
        return self.frameStyle() == QFrame.Shape.NoFrame and not self.autoFillBackground()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def setExpanded(self, expanded: bool):
        self._is_expanded = expanded
        self.updateIcon()

    def isExpanded(self) -> bool:
        return self._is_expanded

    def setIconStyle(self, style: IndicatorStyle):
        """Define o estilo do ícone: 'arrow' ou 'plus_minus'."""
        if style in [QAccordionHeader.IndicatorStyle.Arrow, QAccordionHeader.IndicatorStyle.PlusMinus]:
            self._icon_style = style
            self.updateIcon()

    def updateIcon(self):
        """Atualiza o ícone usando QAutoIcon para garantir cores dinâmicas."""
        icon_name = ""

        if self._icon_style == QAccordionHeader.IndicatorStyle.Arrow:
            icon_name = "fa6s.angle-down" if self._is_expanded else "fa6s.angle-right"

        elif self._icon_style == QAccordionHeader.IndicatorStyle.PlusMinus:
            icon_name = "fa6s.minus" if self._is_expanded else "fa6s.plus"

        # --- AQUI ESTA A MAGICA ---
        # Usamos o método estático que adicionamos ao QAutoIcon
        if icon_name:
            self._btn_icon.setIcon(QThemeResponsiveIcon.fromAwesome(icon_name))

    def setIconPosition(self, position: IconPosition):
        if position in [QAccordionHeader.IconPosition.TrailingPosition, QAccordionHeader.IconPosition.LeadingPosition]:
            self._icon_position = position
            self.refreshLayout()

    def refreshLayout(self):
        while self._layout_header.count():
            self._layout_header.takeAt(0)

        if self._icon_position == QAccordionHeader.IconPosition.LeadingPosition:
            self._layout_header.addWidget(self._btn_icon)
            self._layout_header.addWidget(self._label_title)
            self._label_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        elif self._icon_position == QAccordionHeader.IconPosition.TrailingPosition:
            self._label_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self._layout_header.addWidget(self._label_title)
            self._layout_header.addWidget(self._btn_icon)

    def setTitle(self, title: str):
        self._label_title.setText(title)

    def titleLabel(self) -> QLabel:
        return self._label_title

    def iconWidget(self) -> QWidget:
        # Renomeei de iconLabel para iconWidget pois agora é um botão
        return self._btn_icon


class QAccordionItem(QWidget):
    def __init__(self, title, content_widget):
        super().__init__()
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._header = QAccordionHeader(title)
        self._content = content_widget
        self._content.setVisible(False)

        self._layout.addWidget(self._header)
        self._layout.addWidget(self._content)

        self._header.clicked.connect(self.toggle)

    def toggle(self):
        self.setExpanded(not self._content.isVisible())

    def setExpanded(self, expanded):
        self._header.setExpanded(expanded)
        self._content.setVisible(expanded)

    def isExpanded(self):
        return self._header.isExpanded() and self._content.isVisible()

    def setIconPosition(self, position: QAccordionHeader.IconPosition):
        self._header.setIconPosition(position)

    def setIconStyle(self, style: QAccordionHeader.IndicatorStyle):
        self._header.setIconStyle(style)

    def setFlat(self, flat: bool):
        self._header.setFlat(flat)

    def content(self) -> QWidget:
        return self._content

    def header(self) -> QAccordionHeader:
        return self._header