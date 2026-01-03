from enum import IntEnum, auto

from PySide6.QtCore import Signal, QSize, QPropertyAnimation, QEasingCurve, QAbstractAnimation, Property
from PySide6.QtGui import Qt, QMouseEvent
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QFrame, QSizePolicy, QVBoxLayout, QToolButton, QLineEdit

from qextrawidgets.icons import QThemeResponsiveIcon


class QAccordionHeader(QFrame):
    clicked = Signal()

    IconPosition = QLineEdit.ActionPosition

    class IndicatorStyle(IntEnum):
        Arrow = auto()  # Arrow (> v)
        PlusMinus = auto()  # Plus/Minus (+ -)

    def __init__(self, title="", parent=None):
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
        self._btn_icon = QToolButton()
        self._btn_icon.setFixedSize(24, 24)
        self._btn_icon.setIconSize(QSize(16, 16))  # Icon drawing size
        self._btn_icon.setAutoRaise(True)  # Remove button borders

        # Important: The button must ignore the mouse so that the click
        # is captured by the Header (QFrame) and not "stolen" by the button.
        self._btn_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Layout
        self._layout_header = QHBoxLayout(self)
        self._layout_header.setContentsMargins(10, 5, 10, 5)

        # Initialization
        self.updateIcon()
        self.refreshLayout()
        self.setFlat(False)

    def setFlat(self, flat: bool):
        """
        Defines whether the header looks like a raised button (False) or plain text (True).
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
        if style in [QAccordionHeader.IndicatorStyle.Arrow, QAccordionHeader.IndicatorStyle.PlusMinus]:
            self._icon_style = style
            self.updateIcon()

    def updateIcon(self):
        """Updates the icon using QThemeResponsiveIcon to ensure dynamic colors."""
        icon_name = ""

        if self._icon_style == QAccordionHeader.IndicatorStyle.Arrow:
            icon_name = "fa6s.angle-down" if self._is_expanded else "fa6s.angle-right"

        elif self._icon_style == QAccordionHeader.IndicatorStyle.PlusMinus:
            icon_name = "fa6s.minus" if self._is_expanded else "fa6s.plus"

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
        # Renamed from iconLabel because it is now a button
        return self._btn_icon


class QAccordionItem(QWidget):
    """
    Accordion item with optional smooth expand/collapse animation.
    """

    def __init__(self, title: str, content_widget: QWidget):
        super().__init__()
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
        self._layout.addWidget(self._content, True, Qt.AlignmentFlag.AlignTop)

        self._header.clicked.connect(self.toggle)

    def toggle(self):
        """Toggles the expanded state."""
        self.setExpanded(not self.isExpanded())

    def setExpanded(self, expanded: bool, animated: bool = None):
        """
        Sets the expanded state.

        :param expanded: True to expand, False to collapse
        :param animated: Override animation setting for this call. If None, uses the widget's setting.
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
                print(f"Target Height: {target_height}")

                # Animate from 0 to target height
                self._animation.setStartValue(0)
                self._animation.setEndValue(target_height)
                self._animation.start()
        else:
            # Collapsing
            if use_animation:
                # Get current height
                current_height = self._content.height()
                print(f"Current Height: {current_height}")

                # Animate from current height to 0
                self._animation.setStartValue(current_height)
                self._animation.setEndValue(0)
                self._animation.finished.connect(self._on_collapse_finished)
                self._animation.start()
            else:
                # Instant collapse
                self._content.setVisible(False)


    def _on_collapse_finished(self):
        """Called when collapse animation finishes."""
        self._animation.finished.disconnect(self._on_collapse_finished)
        self._content.setVisible(False)

    def isExpanded(self) -> bool:
        """Returns True if the item is expanded."""
        return self._header.isExpanded()

    # --- Animation Settings ---

    def setAnimationEnabled(self, enabled: bool):
        """Enable or disable animations."""
        self._animation_enabled = enabled

    def animationEnabled(self) -> bool:
        """Returns True if animations are enabled."""
        return self._animation_enabled

    def setAnimationDuration(self, duration: int):
        """
        Sets the animation duration in milliseconds.

        :param duration: Duration in milliseconds (typical range: 100-500)
        """
        self._animation_duration = duration
        self._animation.setDuration(duration)

    def animationDuration(self) -> int:
        """Returns the animation duration in milliseconds."""
        return self._animation_duration

    def setAnimationEasing(self, easing: QEasingCurve.Type):
        """
        Sets the animation easing curve.

        :param easing: QEasingCurve.Type (e.g., InOutQuart, OutCubic, Linear)
        """
        self._animation_easing = easing
        self._animation.setEasingCurve(easing)

    def animationEasing(self) -> QEasingCurve.Type:
        """Returns the animation easing curve."""
        return self._animation_easing

    # --- Style Settings ---

    def setIconPosition(self, position: QAccordionHeader.IconPosition):
        """Sets the icon position (Leading or Trailing)."""
        self._header.setIconPosition(position)

    def setIconStyle(self, style: QAccordionHeader.IndicatorStyle):
        """Sets the icon style (Arrow or PlusMinus)."""
        self._header.setIconStyle(style)

    def setFlat(self, flat: bool):
        """Sets whether the header is flat or raised."""
        self._header.setFlat(flat)

    # --- Accessors ---

    def content(self) -> QWidget:
        """Returns the content widget."""
        return self._content

    def header(self) -> QAccordionHeader:
        """Returns the header widget."""
        return self._header