import typing

from PySide6.QtWidgets import QPushButton, QStyleOptionButton, QStyle
from PySide6.QtGui import QPalette, QColor


class QColorButton(QPushButton):
    def __init__(self, text, color, text_color = "auto", parent = None):
        super().__init__(text, parent)

        # We store colors as class attributes
        self._color = None
        self._text_color = None

        self.setColor(color)
        self.setTextColor(text_color)

        # Initial visual configuration
        self.setAutoFillBackground(True)

    def initStyleOption(self, option: QStyleOptionButton):
        """
        Method called automatically by Qt before drawing the button.
        Here we intercept the style option and change the palette color
        based on the current state (Hover, Pressed, etc).
        """
        # 1. Let QPushButton fill the option with the default state
        super().initStyleOption(option)

        state: QStyle.StateFlag = getattr(option, 'state')
        palette: QPalette = getattr(option, 'palette')

        # 2. Check the state in the 'option' object and change the palette color locally
        if state & QStyle.StateFlag.State_Sunken:  # Pressed
            pressed_color = self._color.darker(115)  # 15% darker
            palette.setColor(QPalette.ColorRole.Button, pressed_color)
            palette.setColor(QPalette.ColorRole.Window, pressed_color)  # For background fill

        elif state & QStyle.StateFlag.State_MouseOver:  # Mouse over
            hover_color = self._color.lighter(115)  # 15% lighter
            palette.setColor(QPalette.ColorRole.Button, hover_color)
            palette.setColor(QPalette.ColorRole.Window, hover_color)

        else:  # Normal State
            palette.setColor(QPalette.ColorRole.Button, self._color)
            palette.setColor(QPalette.ColorRole.Window, self._color)

        if self._text_color == "auto":
            palette.setColor(QPalette.ColorRole.ButtonText, self.getContrastingTextColor(self._color))

        else:
            palette.setColor(QPalette.ColorRole.ButtonText, self._text_color)

    def color(self) -> QColor:
        return self._color

    def setColor(self, color):
        if isinstance(color, str):
            self._color = QColor(color)

        elif isinstance(color, QColor):
            self._color = color

    def textColor(self) -> typing.Union[str, QColor]:
        return self._text_color

    def setTextColor(self, text_color):
        if isinstance(text_color, str):
            if text_color == "auto":
                self._text_color = text_color

            else:
                self._text_color = QColor(text_color)

        elif isinstance(text_color, QColor):
            self._text_color = text_color

    @staticmethod
    def getContrastingTextColor(bg_color: QColor) -> QColor:
        """
        Returns Qt.black or Qt.white depending on the background color luminance.
        Formula based on human perception (NTSC conversion formula).
        """
        r = bg_color.red()
        g = bg_color.green()
        b = bg_color.blue()

        # Calculate weighted brightness
        # 0.299R + 0.587G + 0.114B
        luminance = (0.299 * r) + (0.587 * g) + (0.114 * b)

        # Common threshold is 128 (half of 255).
        # If brighter than 128, background is light -> Black Text
        # If darker, background is dark -> White Text
        return QColor("black") if luminance > 128 else QColor("white")
