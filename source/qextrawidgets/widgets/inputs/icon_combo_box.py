import typing

from PySide6.QtWidgets import QToolButton, QMenu, QWidgetAction, QWidget, QVBoxLayout
from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtCore import Qt, QSize, Signal

class QIconComboBox(QToolButton):
    """A widget similar to QComboBox but optimized for icons or short text.

    It maintains a 1:1 aspect ratio and the style of a QToolButton.

    Signals:
        currentIndexChanged (int): Emitted when the current index changes.
        currentDataChanged (object): Emitted when the data of the current item changes.
    """

    currentIndexChanged = Signal(int)
    currentDataChanged = Signal(object)

    def __init__(self, parent: typing.Optional[QWidget] = None, size: int = 40) -> None:
        """Initializes the icon combo box.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
            size (int, optional): Size of the button (width and height). Defaults to 40.
        """
        super().__init__(parent)

        self._size = size
        self._items = []  # List of dictionaries {'icon': QIcon, 'text': str, 'data': object, 'button': QToolButton}
        self._current_index = -1

        # Main Button Configuration
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.setFixedSize(self._size, self._size)
        self.setStyleSheet("QToolButton::menu-indicator { image: none; }")

        # Create Menu
        self._menu = QMenu(self)
        self.setMenu(self._menu)

        # Internal menu panel
        self._container_action = QWidgetAction(self._menu)
        self._panel = QWidget()
        self._layout = QVBoxLayout(self._panel)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._container_action.setDefaultWidget(self._panel)
        self._menu.addAction(self._container_action)

    def addItem(self, icon: typing.Optional[typing.Union[QIcon, str, QPixmap]] = None, text: typing.Optional[str] = None, data: typing.Any = None, font: typing.Optional[QFont] = None) -> int:
        """Adds an item to the menu.

        Args:
            icon (Union[QIcon, str, QPixmap], optional): Item icon, theme icon name, or QPixmap. Defaults to None.
            text (str, optional): Item text. Defaults to None.
            data (Any, optional): Custom data associated with the item. Defaults to None.
            font (QFont, optional): Custom font for the item. Defaults to None.

        Returns:
            int: The index of the added item.
        """
        index = len(self._items)

        btn_item = QToolButton()
        btn_item.setAutoRaise(True)
        btn_item.setFixedSize(self._size, self._size)

        if font:
            btn_item.setFont(font)
        else:
            btn_item.setFont(self.font())

        if icon:
            if isinstance(icon, QPixmap):
                icon = QIcon(icon)
            elif isinstance(icon, str):
                icon = QIcon.fromTheme(icon)
            btn_item.setIcon(icon)
            btn_item.setIconSize(QSize(int(self._size * 0.6), int(self._size * 0.6)))
        elif text:
            btn_item.setText(text)
            btn_item.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)

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

    def setCurrentIndex(self, index: int) -> None:
        """Sets the current index and updates the main button.

        Args:
            index (int): Index to set as current.
        """
        if 0 <= index < len(self._items):
            self._current_index = index
            item = self._items[index]

            if item['font']:
                self.setFont(item['font'])
            else:
                self.setFont(self._panel.font())  # Reset to default font if none specified

            if item['icon']:
                self.setIcon(item['icon'])
                self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            elif item['text']:
                self.setText(item['text'])
                self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)

            self.currentIndexChanged.emit(index)
            self.currentDataChanged.emit(item['data'])
        elif index == -1:
            self._current_index = -1
            self.setIcon(QIcon())
            self.setText("")

    def currentIndex(self) -> int:
        """Returns the current index.

        Returns:
            int: Current index.
        """
        return self._current_index

    def currentData(self) -> typing.Any:
        """Returns the data associated with the current item.

        Returns:
            Any: Current item data or None.
        """
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index]['data']
        return None

    def itemData(self, index: int) -> typing.Any:
        """Returns the data associated with the item at the given index.

        Args:
            index (int): Item index.

        Returns:
            Any: Item data or None.
        """
        if 0 <= index < len(self._items):
            return self._items[index]['data']
        return None

    def setItemFont(self, index: int, font: QFont) -> None:
        """Sets the font for the item at the given index.

        Args:
            index (int): Item index.
            font (QFont): New font.
        """
        if 0 <= index < len(self._items):
            self._items[index]['font'] = font
            self._items[index]['button'].setFont(font)
            if index == self._current_index:
                self.setFont(font)

    def itemFont(self, index: int) -> typing.Optional[QFont]:
        """Returns the font of the item at the given index.

        Args:
            index (int): Item index.

        Returns:
            QFont, optional: Item font or None.
        """
        if 0 <= index < len(self._items):
            return self._items[index]['font']
        return None

    def setItemText(self, index: int, text: str) -> None:
        """Sets the text for the item at the given index.

        Args:
            index (int): Item index.
            text (str): New text.
        """
        if 0 <= index < len(self._items):
            self._items[index]['text'] = text
            btn = self._items[index]['button']
            btn.setText(text)
            if not self._items[index]['icon']:
                btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)

            if index == self._current_index:
                self.setCurrentIndex(index)

    def itemText(self, index: int) -> str:
        """Returns the text of the item at the given index.

        Args:
            index (int): Item index.

        Returns:
            str: Item text.
        """
        if 0 <= index < len(self._items):
            return self._items[index]['text']
        return ""

    def setItemIcon(self, index: int, icon: typing.Optional[typing.Union[QIcon, str, QPixmap]]) -> None:
        """Sets the icon for the item at the given index.

        Args:
            index (int): Item index.
            icon (Union[QIcon, str, QPixmap], optional): New icon, theme icon name, or QPixmap.
        """
        if 0 <= index < len(self._items):
            if isinstance(icon, QPixmap):
                icon = QIcon(icon)
            elif isinstance(icon, str):
                icon = QIcon.fromTheme(icon)

            self._items[index]['icon'] = icon
            btn = self._items[index]['button']

            if icon:
                btn.setIcon(icon)
                btn.setIconSize(QSize(int(self._size * 0.6), int(self._size * 0.6)))
                btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            else:
                btn.setIcon(QIcon())
                if self._items[index]['text']:
                    btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)

            if index == self._current_index:
                self.setCurrentIndex(index)

    def itemIcon(self, index: int) -> QIcon:
        """Returns the icon of the item at the given index.

        Args:
            index (int): Item index.

        Returns:
            QIcon: Item icon.
        """
        if 0 <= index < len(self._items):
            return self._items[index]['icon']
        return QIcon()

    def setItemData(self, index: int, data: typing.Any) -> None:
        """Sets the data associated with the item at the given index.

        Args:
            index (int): Item index.
            data (Any): New data.
        """
        if 0 <= index < len(self._items):
            self._items[index]['data'] = data
            if index == self._current_index:
                self.currentDataChanged.emit(data)

    def count(self) -> int:
        """Returns the number of items in the combo box.

        Returns:
            int: Number of items.
        """
        return len(self._items)

    def clear(self) -> None:
        """Removes all items from the combo box."""
        self._items = []
        self._current_index = -1
        # Clear layout
        while self._layout.count():
            child = self._layout.takeAt(0)
            if child:
                widget = child.widget()
                if widget:
                    widget.deleteLater()
            else:
                break
        self.setIcon(QIcon())
        self.setText("")
