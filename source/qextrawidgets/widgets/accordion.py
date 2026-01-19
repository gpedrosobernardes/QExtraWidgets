from PySide6.QtCore import Qt, Signal, QEasingCurve
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame

from qextrawidgets.widgets.accordion_item import QAccordionItem, QAccordionHeader


class QAccordion(QWidget):
    """Accordion widget with optional smooth animations.

    Supports multiple accordion items with expand/collapse animations.

    Signals:
        enteredSection (QAccordionItem): Emitted when a section is scrolled into view.
        leftSection (QAccordionItem): Emitted when a section is scrolled out of view.
    """

    enteredSection = Signal(QAccordionItem)
    leftSection = Signal(QAccordionItem)

    def __init__(self, parent: QWidget = None) -> None:
        """Initializes the accordion widget.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._scroll_content = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_content)
        self._scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._scroll.setWidget(self._scroll_content)
        self._main_layout.addWidget(self._scroll)

        self._active_section = None
        self._items = []

        # Animation settings (applied to new items)
        self._default_animation_enabled = True
        self._default_animation_duration = 200
        self._default_animation_easing = QEasingCurve.Type.InOutQuart

        self._setup_connections()

    def _setup_connections(self) -> None:
        """Sets up signals and slots connections."""
        self._scroll.verticalScrollBar().valueChanged.connect(self._on_scroll)

    def _on_scroll(self, value: int) -> None:
        """Handles scroll value changes.

        Args:
            value (int): Current scroll value.
        """
        for item in self._items:
            if item.y() <= value <= item.y() + item.height() and item != self._active_section:
                self.enteredSection.emit(item)
                if self._active_section is not None:
                    self.leftSection.emit(item)
                self._active_section = item
                break

    def _on_item_expanded(self, position: int, expanded: bool) -> None:
        """Called when an item is expanded.

        Args:
            position (int): Position of the item.
            expanded (bool): Whether the item is expanded.
        """
        self._scroll_layout.setStretch(position, expanded)

    # --- Item Management ---

    def setSectionTitle(self, index: int, title: str) -> None:
        """Sets the title of the section at the given index.

        Args:
            index (int): Index of the section.
            title (str): New title for the section.
        """
        self._items[index].setTitle(title)

    def addSection(self, title: str, widget: QWidget) -> QAccordionItem:
        """Creates and adds a new accordion section at the end.

        Args:
            title (str): Section title.
            widget (QWidget): Content widget.

        Returns:
            QAccordionItem: The created accordion item.
        """
        return self.insertSection(title, widget)

    def addAccordionItem(self, item: QAccordionItem) -> None:
        """Adds an existing accordion item at the end.

        Args:
            item (QAccordionItem): Accordion item to add.
        """
        self.insertAccordionItem(item)

    def insertSection(self, title: str, widget: QWidget, position: int = -1) -> QAccordionItem:
        """Creates and inserts a new accordion section.

        Args:
            title (str): Section title.
            widget (QWidget): Content widget.
            position (int, optional): Insert position (-1 for end). Defaults to -1.

        Returns:
            QAccordionItem: The created accordion item.
        """
        item = QAccordionItem(title, widget)
        # Apply default animation settings
        item.setAnimationEnabled(self._default_animation_enabled)
        item.setAnimationDuration(self._default_animation_duration)
        item.setAnimationEasing(self._default_animation_easing)

        self.insertAccordionItem(item, position)
        return item

    def insertAccordionItem(self, item: QAccordionItem, position: int = -1) -> None:
        """Inserts an existing accordion item.

        Args:
            item (QAccordionItem): Accordion item to insert.
            position (int, optional): Insert position (-1 for end). Defaults to -1.
        """
        self._scroll_layout.insertWidget(position, item)
        item.expandedChanged.connect(lambda expanded: self._on_item_expanded(position, expanded))
        self._items.append(item)

    def removeAccordionItem(self, item: QAccordionItem) -> None:
        """Removes an accordion item.

        Args:
            item (QAccordionItem): Accordion item to remove.
        """
        self._scroll_layout.removeWidget(item)
        self._items.remove(item)

    # --- Style Settings (Applied to ALL items) ---

    def setIconPosition(self, position: QAccordionHeader.IconPosition) -> None:
        """Changes the icon position of all items.

        Args:
            position (QAccordionHeader.IconPosition): New icon position.
        """
        for item in self._items:
            item.setIconPosition(position)

    def setIconStyle(self, style: QAccordionHeader.IndicatorStyle) -> None:
        """Changes the icon style of all items.

        Args:
            style (QAccordionHeader.IndicatorStyle): New icon style.
        """
        for item in self._items:
            item.setIconStyle(style)

    def setFlat(self, flat: bool) -> None:
        """Sets whether headers are flat or raised for all items.

        Args:
            flat (bool): True for flat headers, False for raised.
        """
        for item in self._items:
            item.setFlat(flat)

    # --- Animation Settings (Applied to ALL items) ---

    def setAnimationEnabled(self, enabled: bool) -> None:
        """Enables or disables animations for all items.

        Args:
            enabled (bool): True to enable animations, False to disable.
        """
        self._default_animation_enabled = enabled
        for item in self._items:
            item.setAnimationEnabled(enabled)

    def isAnimationEnabled(self) -> bool:
        """Checks if animations are enabled by default.

        Returns:
            bool: True if animations are enabled, False otherwise.
        """
        return self._default_animation_enabled

    def setAnimationDuration(self, duration: int) -> None:
        """Sets the animation duration in milliseconds for all items.

        Args:
            duration (int): Duration in milliseconds (typical: 100-500).
        """
        self._default_animation_duration = duration
        for item in self._items:
            item.setAnimationDuration(duration)

    def animationDuration(self) -> int:
        """Returns the default animation duration.

        Returns:
            int: Animation duration in milliseconds.
        """
        return self._default_animation_duration

    def setAnimationEasing(self, easing: QEasingCurve.Type) -> None:
        """Sets the animation easing curve for all items.

        Args:
            easing (QEasingCurve.Type): The easing curve type.
        """
        self._default_animation_easing = easing
        for item in self._items:
            item.setAnimationEasing(easing)

    def animationEasing(self) -> QEasingCurve.Type:
        """Returns the default animation easing curve.

        Returns:
            QEasingCurve.Type: The easing curve type.
        """
        return self._default_animation_easing

    # --- Expand/Collapse Operations ---

    def expandAll(self, animated: bool = None) -> None:
        """Expands all accordion items.

        Args:
            animated (bool, optional): Override animation setting. If None, uses each item's setting. Defaults to None.
        """
        for item in self._items:
            item.setExpanded(True, animated=animated)

    def collapseAll(self, animated: bool = None) -> None:
        """Collapses all accordion items.

        Args:
            animated (bool, optional): Override animation setting. If None, uses each item's setting. Defaults to None.
        """
        for item in self._items:
            item.setExpanded(False, animated=animated)

    # --- Scroll Operations ---

    def scrollToItem(self, target_item: QAccordionItem) -> None:
        """Scrolls to make the target item visible.

        Args:
            target_item (QAccordionItem): The item to scroll to.
        """
        # Gets the Y coordinate of the target widget relative to the ScrollArea content
        y_pos = target_item.y()
        # Sets the vertical scroll bar value
        self._scroll.verticalScrollBar().setValue(y_pos)

    def resetScroll(self) -> None:
        """Scrolls to the top of the accordion."""
        self._scroll.verticalScrollBar().setValue(0)