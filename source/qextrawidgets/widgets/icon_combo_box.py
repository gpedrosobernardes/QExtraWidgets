import typing

from PySide6.QtWidgets import QToolButton, QMenu, QWidgetAction, QWidget, QVBoxLayout
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, QSize, Signal

class QIconComboBox(QToolButton):
    """
    Um widget semelhante ao QComboBox, mas otimizado para ícones ou textos curtos
    mantendo uma proporção 1:1 e o estilo de um QToolButton.
    """
    
    currentIndexChanged = Signal(int)
    currentDataChanged = Signal(object)

    def __init__(self, parent=None, size=40):
        super().__init__(parent)
        
        self._size = size
        self._items = []  # Lista de dicionários {'icon': QIcon, 'text': str, 'data': object, 'button': QToolButton}
        self._current_index = -1
        
        # Configuração do Botão Principal
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.setFixedSize(self._size, self._size)
        self.setStyleSheet("QToolButton::menu-indicator { image: none; }")
        
        # Criar o Menu
        self._menu = QMenu(self)
        self.setMenu(self._menu)
        
        # Painel interno do menu
        self._container_action = QWidgetAction(self._menu)
        self._panel = QWidget()
        self._layout = QVBoxLayout(self._panel)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        
        self._container_action.setDefaultWidget(self._panel)
        self._menu.addAction(self._container_action)

    def addItem(self, icon=None, text=None, data=None, font=None):
        """Adiciona um item ao menu."""
        index = len(self._items)
        
        btn_item = QToolButton()
        btn_item.setAutoRaise(True)
        btn_item.setFixedSize(self._size, self._size)
        
        if font:
            btn_item.setFont(font)
        
        if icon:
            if isinstance(icon, str):
                icon = QIcon.fromTheme(icon)
            btn_item.setIcon(icon)
            btn_item.setIconSize(QSize(int(self._size * 0.6), int(self._size * 0.6)))
        elif text:
            btn_item.setText(text)
            btn_item.setToolButtonStyle(Qt.ToolButtonTextOnly)
        
        btn_item.clicked.connect(lambda: self.setCurrentIndex(index))
        btn_item.clicked.connect(self._menu.close)
        
        self._layout.addWidget(btn_item)
        
        item_info = {
            'icon': icon,
            'text': text,
            'data': data,
            'font': font,
            'button': btn_item
        }
        self._items.append(item_info)
        
        if self._current_index == -1:
            self.setCurrentIndex(0)
            
        return index

    def setCurrentIndex(self, index: int):
        """Define o índice atual e atualiza o botão principal."""
        if 0 <= index < len(self._items):
            self._current_index = index
            item = self._items[index]
            
            if item['font']:
                self.setFont(item['font'])
            else:
                self.setFont(self._panel.font()) # Reset para fonte padrão se não tiver específica
            
            if item['icon']:
                self.setIcon(item['icon'])
                self.setToolButtonStyle(Qt.ToolButtonIconOnly)
            elif item['text']:
                self.setText(item['text'])
                self.setToolButtonStyle(Qt.ToolButtonTextOnly)
                
            self.currentIndexChanged.emit(index)
            self.currentDataChanged.emit(item['data'])
        elif index == -1:
            self._current_index = -1
            self.setIcon(QIcon())
            self.setText("")

    def currentIndex(self) -> int:
        return self._current_index

    def currentData(self):
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index]['data']
        return None

    def itemData(self, index: int):
        if 0 <= index < len(self._items):
            return self._items[index]['data']
        return None

    def setItemFont(self, index: int, font: QFont):
        if 0 <= index < len(self._items):
            self._items[index]['font'] = font
            self._items[index]['button'].setFont(font)
            if index == self._current_index:
                self.setFont(font)

    def itemFont(self, index: int) -> QFont:
        if 0 <= index < len(self._items):
            return self._items[index]['font']
        return None

    def setItemText(self, index: int, text: str):
        if 0 <= index < len(self._items):
            self._items[index]['text'] = text
            btn = self._items[index]['button']
            btn.setText(text)
            if not self._items[index]['icon']:
                btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
            
            if index == self._current_index:
                self.setCurrentIndex(index)

    def itemText(self, index: int) -> str:
        if 0 <= index < len(self._items):
            return self._items[index]['text']
        return ""

    def setItemIcon(self, index: int, icon: typing.Optional[typing.Union[QIcon, str]]):
        if 0 <= index < len(self._items):
            if isinstance(icon, str):
                icon = QIcon.fromTheme(icon)
            
            self._items[index]['icon'] = icon
            btn = self._items[index]['button']
            
            if icon:
                btn.setIcon(icon)
                btn.setIconSize(QSize(int(self._size * 0.6), int(self._size * 0.6)))
                btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
            else:
                btn.setIcon(QIcon())
                if self._items[index]['text']:
                    btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
            
            if index == self._current_index:
                self.setCurrentIndex(index)

    def itemIcon(self, index: int) -> QIcon:
        if 0 <= index < len(self._items):
            return self._items[index]['icon']
        return QIcon()

    def setItemData(self, index: int, data: object):
        if 0 <= index < len(self._items):
            self._items[index]['data'] = data
            if index == self._current_index:
                self.currentDataChanged.emit(data)

    def count(self) -> int:
        return len(self._items)

    def clear(self):
        """Remove todos os itens."""
        self._items = []
        self._current_index = -1
        # Limpar layout
        while self._layout.count():
            child = self._layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.setIcon(QIcon())
        self.setText("")
