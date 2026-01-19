from enum import IntEnum, auto

from PySide6.QtCore import Signal, QSize, QPropertyAnimation, QEasingCurve, QAbstractAnimation, Property
from PySide6.QtGui import Qt, QMouseEvent
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QFrame, QSizePolicy, QVBoxLayout, QToolButton, QLineEdit, QApplication

from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.widgets.theme_responsive_label import QThemeResponsiveLabel


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

    def __init__(self, title: str = "", parent: QWidget = None) -> None:
        """Initializes the accordion header.

        Args:
            title (str, optional): Header title. Defaults to "".
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)

        # Native visual style
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        # States
        self._is_expanded = False
        self._icon_position = QAccordionHeader.IconPosition.LeadingPosition
        self._icon_style = QAccordionHeader.IndicatorStyle.Arrow

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
        self.setFlat(False)

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


class QAccordionItem(QWidget):
    """Accordion item with optional smooth expand/collapse animation.

    Signals:
        expandedChanged (bool): Emitted when the expanded state changes.
    """

    expandedChanged = Signal(bool)

    def __init__(self, title: str, content_widget: QWidget, parent: QWidget = None) -> None:
        """Initializes the accordion item.

        Args:
            title (str): Section title.
            content_widget (QWidget): Content widget to be shown/hidden.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._header = QAccordionHeader(title)
        self._content = content_widget

        # Animation setup
        self._animation_enabled = True
        self._animation_duration = 200  # milliseconds
        self._animation_easing = QEasingCurve.Type.InOutQuart

        # Animation object
        self._animation = QPropertyAnimation(self._content, b"maximumHeight")
        self._animation.setDuration(self._animation_duration)
        self._animation.setEasingCurve(self._animation_easing)

        # Initial state
        self._content.setMinimumHeight(0)
        self._content.setVisible(False)

        self._layout.addWidget(self._header, Qt.AlignmentFlag.AlignTop)
        self._layout.addWidget(self._content, Qt.AlignmentFlag.AlignTop)

        self._header.clicked.connect(self.toggle)

    def toggle(self) -> None:
        """Toggles the expanded state."""
        self.setExpanded(not self.isExpanded())

    def setTitle(self, text: str) -> None:
        """Sets the item title.

        Args:
            text (str): New title text.
        """
        self.header().setTitle(text)

    def setExpanded(self, expanded: bool, animated: bool = None) -> None:
        """Sets the expanded state.

        Args:
            expanded (bool): True to expand, False to collapse.
            animated (bool, optional): Override animation setting for this call. If None, uses the widget's setting. Defaults to None.
        """
        # Determine if we should animate
        use_animation = self._animation_enabled if animated is None else animated

        # Stop any running animation
        if self._animation.state() == QAbstractAnimation.State.Running:
            self._animation.stop()

        # Update header state
        self._header.setExpanded(expanded)

        if expanded:
            # Expanding
            self._content.setVisible(True)

            if use_animation:
                target_height = self._content.sizeHint().height()

                # Animate from 0 to target height
                self._animation.setStartValue(0)
                self._animation.setEndValue(target_height)
                self._animation.start()
        else:
            # Collapsing
            if use_animation:
                # Get current height
                current_height = self._content.height()

                # Animate from current height to 0
                self._animation.setStartValue(current_height)
                self._animation.setEndValue(0)
                self._animation.finished.connect(self._on_collapse_finished)
                self._animation.start()
            else:
                # Instant collapse
                self._content.setVisible(False)
        self.expandedChanged.emit(expanded)

    def _on_collapse_finished(self) -> None:
        """Called when collapse animation finishes."""
        self._animation.finished.disconnect(self._on_collapse_finished)
        self._content.setVisible(False)

    def isExpanded(self) -> bool:
        """Returns whether the item is expanded.

        Returns:
            bool: True if expanded, False otherwise.
        """
        return self._header.isExpanded()

    # --- Animation Settings ---

    def setAnimationEnabled(self, enabled: bool) -> None:
        """Enable or disable animations.

        Args:
            enabled (bool): True to enable animations, False to disable.
        """
        self._animation_enabled = enabled

    def isAnimationEnabled(self) -> bool:
        """Returns whether animations are enabled.

        Returns:
            bool: True if animations are enabled, False otherwise.
        """
        return self._animation_enabled

    def setAnimationDuration(self, duration: int) -> None:
        """Sets the animation duration in milliseconds.

        Args:
            duration (int): Duration in milliseconds (typical range: 100-500).
        """
        self._animation_duration = duration
        self._animation.setDuration(duration)

    def animationDuration(self) -> int:
        """Returns the animation duration in milliseconds.

        Returns:
            int: Animation duration.
        """
        return self._animation_duration

    def setAnimationEasing(self, easing: QEasingCurve.Type) -> None:
        """Sets the animation easing curve.

        Args:
            easing (QEasingCurve.Type): QEasingCurve.Type (e.g., InOutQuart, OutCubic, Linear).
        """
        self._animation_easing = easing
        self._animation.setEasingCurve(easing)

    def animationEasing(self) -> QEasingCurve.Type:
        """Returns the animation easing curve.

        Returns:
            QEasingCurve.Type: The easing curve.
        """
        return self._animation_easing

    # --- Style Settings ---

    def setIconPosition(self, position: QAccordionHeader.IconPosition) -> None:
        """Sets the icon position.

        Args:
            position (QAccordionHeader.IconPosition): Position (Leading or Trailing).
        """
        self._header.setIconPosition(position)

    def setIconStyle(self, style: QAccordionHeader.IndicatorStyle) -> None:
        """Sets the icon style.

        Args:
            style (QAccordionHeader.IndicatorStyle): Icon style (Arrow or PlusMinus).
        """
        self._header.setIconStyle(style)

    def setFlat(self, flat: bool) -> None:
        """Sets whether the header is flat or raised.

        Args:
            flat (bool): True for flat, False for raised.
        """
        self._header.setFlat(flat)

    # --- Accessors ---

    def content(self) -> QWidget:
        """Returns the content widget.

        Returns:
            QWidget: Content widget.
        """
        return self._content

    def header(self) -> QAccordionHeader:
        """Returns the header widget.

        Returns:
            QAccordionHeader: Header widget.
        """
        return self._header