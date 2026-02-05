from PySide6.QtCore import Qt
import typing

from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QToolButton, QStyleOptionToolButton, QStyle, QWidget

from qextrawidgets.core.utils.color_utils import QColorUtils


class QColorToolButton(QToolButton):
    """A tool button that displays a specific color and automatically adjusts its text color for contrast."""

    def __init__(self,
                 color: typing.Union[Qt.GlobalColor, QColor, str],
                 text: str = "",
                 text_color: typing.Union[Qt.GlobalColor, QColor, str, None] = None,
                 checked_color: typing.Union[Qt.GlobalColor, QColor, str, None] = None,
                 parent: typing.Optional[QWidget] = None) -> None:
        """Initializes the color tool button.

        Args:
            color (Qt.GlobalColor, QColor, str): Background color of the button.
            text (str, optional): Button text. Defaults to "".
            text_color (Qt.GlobalColor, QColor, str, optional): Text color. If None, it's calculated for contrast. Defaults to None.
            checked_color (Qt.GlobalColor, QColor, str, optional): Color when the button is in checked state. Defaults to None.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setText(text)

        # We store colors as class attributes
        self._color: QColor
        self._text_color: typing.Optional[QColor]
        self._checked_color: typing.Optional[QColor]

        self.setColor(color)
        self.setTextColor(text_color)
        self.setCheckedColor(checked_color)

    def initStyleOption(self, option: QStyleOptionToolButton) -> None:
        """Method called automatically by Qt before drawing the button.

        Here we intercept the style option and change the palette color
        based on the current state (Hover, Pressed, etc).

        Args:
            option (QStyleOptionToolButton): The style option to initialize.
        """
        # 1. Let QToolButton fill the option with the default state
        super().initStyleOption(option)

        state: QStyle.StateFlag = getattr(option, 'state')
        palette: QPalette = getattr(option, 'palette')

        # Determine the base color to use (Normal or Checked)
        base_color = self._color
        if (state & QStyle.StateFlag.State_On) and self._checked_color is not None:
            base_color = self._checked_color

        # 2. Check the state in the 'option' object and change the palette color locally
        if state & QStyle.StateFlag.State_Sunken:  # Pressed
            pressed_color = base_color.darker(115)  # 15% darker
            palette.setColor(QPalette.ColorRole.Button, pressed_color)

        elif state & QStyle.StateFlag.State_MouseOver:  # Mouse over
            hover_color = base_color.lighter(115)  # 15% lighter
            palette.setColor(QPalette.ColorRole.Button, hover_color)

        else:  # Normal State (or Checked State if not interacting)
            palette.setColor(QPalette.ColorRole.Button, base_color)

        if self._text_color is None:
            palette.setColor(QPalette.ColorRole.ButtonText, QColorUtils.getContrastingTextColor(base_color))

        else:
            palette.setColor(QPalette.ColorRole.ButtonText, self._text_color)

    def color(self) -> QColor:
        """Returns the button background color.

        Returns:
            QColor: Background color.
        """
        return self._color

    def setColor(self, color: typing.Union[Qt.GlobalColor, QColor, str]) -> None:
        """Sets the button background color.

        Args:
            color (Qt.GlobalColor, QColor, str): New background color.
        """
        self._color = QColor(color)

    def checkedColor(self) -> typing.Optional[QColor]:
        """Returns the color used when the button is checked.

        Returns:
            QColor, optional: Checked color or None.
        """
        return self._checked_color

    def setCheckedColor(self, color: typing.Union[Qt.GlobalColor, QColor, str, None]) -> None:
        """Sets the color to use when the button is checked.

        Args:
            color (Qt.GlobalColor, QColor, str, None): New checked color.
        """
        if color is None:
            self._checked_color = None
        else:
            self._checked_color = QColor(color)

    def textColor(self) -> typing.Optional[QColor]:
        """Returns the text color.

        Returns:
            QColor, optional: Text color or None if automatically calculated.
        """
        return self._text_color

    def setTextColor(self, text_color: typing.Union[Qt.GlobalColor, QColor, str, None]) -> None:
        """Sets the text color.

        Args:
            text_color (Qt.GlobalColor, QColor, str, None): New text color.
        """
        if text_color is None:
            self._text_color = text_color
        else:
            self._text_color = QColor(text_color)
