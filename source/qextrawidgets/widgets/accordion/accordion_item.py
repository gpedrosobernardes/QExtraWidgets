from PySide6.QtCore import Signal, QPropertyAnimation, QEasingCurve, QAbstractAnimation
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout

from qextrawidgets.widgets.accordion.accordion_header import QAccordionHeader


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

        self._layout.addWidget(self._header, alignment=Qt.AlignmentFlag.AlignTop)
        self._layout.addWidget(self._content, stretch=True, alignment=Qt.AlignmentFlag.AlignTop)

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