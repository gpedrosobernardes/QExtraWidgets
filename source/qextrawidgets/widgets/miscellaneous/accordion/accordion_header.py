from enum import IntEnum, auto
import typing

from PySide6.QtCore import Signal
from PySide6.QtGui import Qt, QMouseEvent
from PySide6.QtWidgets import QFrame, QLineEdit, QWidget, QSizePolicy, QLabel, QHBoxLayout

from qextrawidgets.gui.icons.theme_responsive_icon import QThemeResponsiveIcon
from qextrawidgets.widgets.displays.theme_responsive_label import QThemeResponsiveLabel


class QAccordionHeader(QFrame):
    """Header widget for an accordion item.

    Signals:
        clicked: Emitted when the header is clicked.
    """

    clicked = Signal()

    IconPosition = QLineEdit.ActionPosition

    class IndicatorStyle(IntEnum):
        """Style of the expansion indicator icon."""
        Arrow = auto()  # Arrow (> v)
        PlusMinus = auto()  # Plus/Minus (+ -)

    def __init__(
            self,
            title: str = "",
            parent: typing.Optional[QWidget] = None,
            flat: bool = False,
            icon_style: IndicatorStyle = IndicatorStyle.Arrow,
            icon_position: IconPosition = IconPosition.LeadingPosition
    ) -> None:
        """Initializes the accordion header.

        Args:
            title (str, optional): Header title. Defaults to "".
            parent (QWidget, optional): Parent widget. Defaults to None.
            flat (bool, optional): Whether the header is flat. Defaults to False.
            icon_style (IndicatorStyle, optional): Icon style. Defaults to Arrow.
            icon_position (IconPosition, optional): Icon position. Defaults to LeadingPosition.
        """
        super().__init__(parent)

        # Native visual style
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        # States
        self._is_expanded = False
        self._icon_position = icon_position
        self._icon_style = icon_style

        # Widgets
        self._label_title = QLabel(title)
        self._label_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # --- CHANGE: We use QToolButton instead of QLabel ---
        # This allows QAutoIcon to manage dynamic painting (colors)
        self._label = QThemeResponsiveLabel()
        self._label.setFixedSize(24, 24)

        # Layout
        self._layout_header = QHBoxLayout(self)
        self._layout_header.setContentsMargins(10, 5, 10, 5)

        # Initialization
        self.updateIcon()
        self.refreshLayout()
        self.setFlat(flat)

    def closeEvent(self, event) -> None:
        """Disconnects signals to prevent crashes on destruction."""
        # QAccordionHeader doesn't have _on_theme_change, it uses QThemeResponsiveLabel
        # So we don't need to disconnect anything here that doesn't exist.
        super().closeEvent(event)

    def setFlat(self, flat: bool) -> None:
        """Defines whether the header looks like a raised button or plain text.

        Args:
            flat (bool): True for flat (plain text), False for raised button.
        """
        if flat:
            self.setFrameStyle(QFrame.Shape.NoFrame)
            self.setAutoFillBackground(False)
        else:
            self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
            self.setAutoFillBackground(True)

    def isFlat(self) -> bool:
        """Returns whether the header is flat.

        Returns:
            bool: True if flat, False otherwise.
        """
        return self.frameStyle() == QFrame.Shape.NoFrame and not self.autoFillBackground()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handles mouse press events.

        Args:
            event (QMouseEvent): Mouse event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def setExpanded(self, expanded: bool) -> None:
        """Sets the expanded state and updates the icon.

        Args:
            expanded (bool): True to show expanded state, False for collapsed.
        """
        self._is_expanded = expanded
        self.updateIcon()

    def isExpanded(self) -> bool:
        """Returns whether the header is in expanded state.

        Returns:
            bool: True if expanded, False otherwise.
        """
        return self._is_expanded

    def setIconStyle(self, style: IndicatorStyle) -> None:
        """Sets the expansion indicator icon style.

        Args:
            style (IndicatorStyle): Icon style (Arrow or PlusMinus).
        """
        if style in [QAccordionHeader.IndicatorStyle.Arrow, QAccordionHeader.IndicatorStyle.PlusMinus]:
            self._icon_style = style
            self.updateIcon()

    def updateIcon(self) -> None:
        """Updates the icon using QThemeResponsiveIcon to ensure dynamic colors."""
        icon_name = ""

        if self._icon_style == QAccordionHeader.IndicatorStyle.Arrow:
            icon_name = "fa6s.angle-down" if self._is_expanded else "fa6s.angle-right"

        elif self._icon_style == QAccordionHeader.IndicatorStyle.PlusMinus:
            icon_name = "fa6s.minus" if self._is_expanded else "fa6s.plus"

        if icon_name:
            self._label.setIcon(QThemeResponsiveIcon.fromAwesome(icon_name))

    def setIconPosition(self, position: IconPosition) -> None:
        """Sets the position of the expansion icon.

        Args:
            position (IconPosition): Position (Leading or Trailing).
        """
        if position in [QAccordionHeader.IconPosition.TrailingPosition, QAccordionHeader.IconPosition.LeadingPosition]:
            self._icon_position = position
            self.refreshLayout()

    def refreshLayout(self) -> None:
        """Refreshes the layout based on icon position."""
        while self._layout_header.count():
            self._layout_header.takeAt(0)

        if self._icon_position == QAccordionHeader.IconPosition.LeadingPosition:
            self._layout_header.addWidget(self._label)
            self._layout_header.addWidget(self._label_title)
            self._label_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        elif self._icon_position == QAccordionHeader.IconPosition.TrailingPosition:
            self._label_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self._layout_header.addWidget(self._label_title)
            self._layout_header.addWidget(self._label)

    def setTitle(self, title: str) -> None:
        """Sets the header title.

        Args:
            title (str): New title text.
        """
        self._label_title.setText(title)

    def titleLabel(self) -> QLabel:
        """Returns the title label widget.

        Returns:
            QLabel: Title label.
        """
        return self._label_title

    def iconWidget(self) -> QWidget:
        """Returns the icon widget.

        Returns:
            QWidget: Icon widget.
        """
        # Renamed from iconLabel because it is now a button
        return self._label
