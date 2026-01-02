import qtawesome
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon, Qt, QMouseEvent
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QFrame, QSizePolicy, QVBoxLayout


class QAccordionHeader(QFrame):
    clicked = Signal()

    def __init__(self, title="", parent=None):
        super().__init__(parent)

        # Estilo visual nativo
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        # Estados
        self._is_expanded = False
        self._icon_position = "left"  # 'left' ou 'right'
        self._icon_style = "arrow"  # 'arrow' ou 'plus_minus'

        # Widgets
        self._label_title = QLabel(title)
        self._label_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._label_icon = QLabel()
        self._label_icon.setFixedSize(24, 24)

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
            # Remove a moldura e a sombra
            self.setFrameStyle(QFrame.Shape.NoFrame)
            # Torna o fundo transparente (opcional, depende do gosto)
            self.setAutoFillBackground(False)
        else:
            # Restaura a aparência de botão/painel
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

    def setIconStyle(self, style: str):
        """Define o estilo do ícone: 'arrow' ou 'plus_minus'."""
        if style in ["arrow", "plus_minus"]:
            self._icon_style = style
            self.updateIcon()

    def updateIcon(self):
        """Atualiza o ícone baseado no estilo atual e no estado (aberto/fechado)."""
        icon = QIcon()

        if self._icon_style == "arrow":
            if self._is_expanded:
                icon = qtawesome.icon("fa6s.angle-down")
            else:
                icon = qtawesome.icon("fa6s.angle-right")

        elif self._icon_style == "plus_minus":
            if self._is_expanded:
                icon = qtawesome.icon("fa6s.minus")
            else:
                icon = qtawesome.icon("fa6s.plus")

        self._label_icon.setPixmap(icon.pixmap(16, 16))

    def setIconPosition(self, position: str):
        if position not in ["left", "right"]:
            return
        self._icon_position = position
        self.refreshLayout()

    def refreshLayout(self):
        while self._layout_header.count():
            self._layout_header.takeAt(0)

        if self._icon_position == "left":
            self._layout_header.addWidget(self._label_icon)
            self._layout_header.addWidget(self._label_title)
            self._label_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        elif self._icon_position == "right":
            self._label_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self._layout_header.addWidget(self._label_title)
            self._layout_header.addWidget(self._label_icon)

    def setTitle(self, title: str):
        self._label_title.setText(title)

    def titleLabel(self) -> QLabel:
        return self._label_title

    def iconLabel(self) -> QLabel:
        return self._label_icon


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

    def setIconPosition(self, position):
        self._header.setIconPosition(position)

    def setIconStyle(self, style):
        self._header.setIconStyle(style)

    def setFlat(self, flat):
        self._header.setFlat(flat)

    def content(self) -> QWidget:
        return self._content

    def header(self) -> QAccordionHeader:
        return self._header