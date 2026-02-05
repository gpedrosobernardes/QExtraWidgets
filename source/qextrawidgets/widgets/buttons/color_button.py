import typing

from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QPushButton, QStyleOptionButton, QStyle, QWidget

from qextrawidgets.core.utils.color_utils import QColorUtils


class QColorButton(QPushButton):
    """A button that displays a specific color and automatically adjusts its text color for contrast."""

    def __init__(self, color: QColor, text: str = "", text_color: QColor = None, checked_color: QColor = None,
                 parent: QWidget = None) -> None:
        """Initializes the color button.

        Args:
            color (QColor): Background color of the button.
            text (str, optional): Button text. Defaults to "".
            text_color (QColor, optional): Text color. If None, it's calculated for contrast. Defaults to None.
            checked_color (QColor, optional): Color when the button is in checked state. Defaults to None.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(text, parent)

        # We store colors as class attributes
        self._color = None
        self._text_color = None
        self._checked_color = None

        self.setColor(color)
        self.setTextColor(text_color)
        self.setCheckedColor(checked_color)

        # Initial visual configuration
        # Removed setAutoFillBackground(True) to avoid square background artifacts on rounded buttons

    def initStyleOption(self, option: QStyleOptionButton) -> None:
        """Method called automatically by Qt before drawing the button.

        Here we intercept the style option and change the palette color
        based on the current state (Hover, Pressed, etc).

        Args:
            option (QStyleOptionButton): The style option to initialize.
        """
        # 1. Let QPushButton fill the option with the default state
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
            # Removed Window role setting as it's not needed for button face and causes artifacts

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

    def setColor(self, color: QColor) -> None:
        """Sets the button background color.

        Args:
            color (QColor): New background color.
        """
        self._color = QColor(color)

    def checkedColor(self) -> typing.Optional[QColor]:
        """Returns the color used when the button is checked.

        Returns:
            QColor, optional: Checked color or None.
        """
        return self._checked_color

    def setCheckedColor(self, color: typing.Union[str, QColor, None]) -> None:
        """Sets the color to use when the button is checked.

        Args:
            color (Union[str, QColor, None]): New checked color.
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

    def setTextColor(self, text_color: typing.Union[str, QColor, None]) -> None:
        """Sets the text color.

        Args:
            text_color (Union[str, QColor, None]): New text color.
        """
        if text_color is None:
            self._text_color = text_color
        else:
            self._text_color = QColor(text_color)
