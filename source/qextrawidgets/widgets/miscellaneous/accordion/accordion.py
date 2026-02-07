import typing
from typing import Optional

from PySide6.QtCore import Qt, Signal, QEasingCurve, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame

from qextrawidgets.widgets.miscellaneous.accordion.accordion_item import QAccordionItem
from qextrawidgets.widgets.miscellaneous.accordion.accordion_header import QAccordionHeader


class QAccordion(QWidget):
    """Accordion widget with optional smooth animations.

    A container that organizes content into collapsible sections.
    Supports multiple accordion items with expand/collapse animations,
    customizable styling (flat/raised, icon style, icon position),
    and vertical alignment control.

    Signals:
        enteredSection (QAccordionItem): Emitted when a section is scrolled into view.
        leftSection (QAccordionItem): Emitted when a section is scrolled out of view.
    """

    enteredSection = Signal(QAccordionItem)
    leftSection = Signal(QAccordionItem)

    def __init__(
            self,
            parent: typing.Optional[QWidget] = None,
            items_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignTop,
            items_flat: bool = False,
            items_icon_style: QAccordionHeader.IndicatorStyle = QAccordionHeader.IndicatorStyle.Arrow,
            items_icon_position: QAccordionHeader.IconPosition = QAccordionHeader.IconPosition.LeadingPosition,
            animation_enabled: bool = False,
            animation_duration: int = 200,
            animation_easing: QEasingCurve.Type = QEasingCurve.Type.InOutQuart
    ) -> None:
        """Initializes the accordion widget.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
            items_alignment (Qt.AlignmentFlag, optional): Vertical alignment of items. Defaults to AlignTop.
            items_flat (bool, optional): Whether items are flat. Defaults to False.
            items_icon_style (QAccordionHeader.IndicatorStyle, optional): Icon style. Defaults to Arrow.
            items_icon_position (QAccordionHeader.IconPosition, optional): Icon position. Defaults to LeadingPosition.
            animation_enabled (bool, optional): Whether animations are enabled. Defaults to False.
            animation_duration (int, optional): Animation duration in ms. Defaults to 200.
            animation_easing (QEasingCurve.Type, optional): Animation easing curve. Defaults to InOutQuart.
        """
        super().__init__(parent)
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._scroll_content = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_content)
        self._scroll_layout.setAlignment(items_alignment)

        self._scroll.setWidget(self._scroll_content)
        self._main_layout.addWidget(self._scroll)

        self._active_section = None
        self._items = []

        # Animation settings (applied to new items)
        self._animation_enabled = animation_enabled
        self._animation_duration = animation_duration
        self._animation_easing = animation_easing

        self._items_alignment = items_alignment
        self._items_flat = items_flat
        self._items_icon_style = items_icon_style
        self._items_icon_position = items_icon_position

        self._setup_connections()

    def _setup_connections(self) -> None:
        """Sets up signals and slots connections."""
        self._scroll.verticalScrollBar().valueChanged.connect(self._on_scroll)

    @Slot(int)
    def _on_scroll(self, value: int) -> None:
        """Handles scroll value changes.

        Args:
            value (int): Current scroll value.
        """
        for item in self._items:
            if item.y() <= value <= item.y() + item.height() and item != self._active_section:
                if self._active_section:
                    self.leftSection.emit(item)
                self._active_section = item
                self.enteredSection.emit(item)
                break

    # --- Item Management ---

    def setSectionTitle(self, index: int, title: str) -> None:
        """Sets the title of the section at the given index.

        Args:
            index (int): Index of the section.
            title (str): New title for the section.
        """
        self._items[index].setTitle(title)

    def addSection(self, title: str, widget: QWidget, name: typing.Optional[str] = None) -> QAccordionItem:
        """Creates and adds a new accordion section at the end.

        Args:
            title (str): Section title.
            widget (QWidget): Content widget.
            name (str, optional): Unique name for the section. Defaults to None.

        Returns:
            QAccordionItem: The created accordion item.
        """
        return self.insertSection(title, widget, name=name)

    def addAccordionItem(self, item: QAccordionItem) -> None:
        """Adds an existing accordion item at the end.

        Args:
            item (QAccordionItem): Accordion item to add.
        """
        self.insertAccordionItem(item)

    def insertSection(self, title: str, widget: QWidget, position: int = -1, expanded: bool = False, name: typing.Optional[str] = None) -> QAccordionItem:
        """Creates and inserts a new accordion section.

        Args:
            title (str): Section title.
            widget (QWidget): Content widget.
            position (int, optional): Insert position (-1 for end). Defaults to -1.
            expanded (bool, optional): Whether the section is expanded. Defaults to False.
            name (str, optional): Unique name for the section. Defaults to None.

        Returns:
            QAccordionItem: The created accordion item.
        """
        item = QAccordionItem(title, widget, self._scroll_content, expanded, self._items_flat, self._items_icon_style, self._items_icon_position, self._animation_enabled, self._animation_duration, self._animation_easing)

        if name:
            item.setObjectName(name)

        self.insertAccordionItem(item, position)
        return item

    def insertAccordionItem(self, item: QAccordionItem, position: int = -1) -> None:
        """Inserts an existing accordion item.

        Args:
            item (QAccordionItem): Accordion item to insert.
            position (int, optional): Insert position (-1 for end). Defaults to -1.
        """
        self._scroll_layout.insertWidget(position, item, alignment=self._items_alignment)
        if position == -1:
            self._items.append(item)
        else:
            self._items.insert(position, item)

        item.expandedChanged.connect(lambda expanded: self._on_item_toggled(item, expanded))

    def _on_item_toggled(self, item: QAccordionItem, expanded: bool) -> None:
        """Handles item toggle events.

        Args:
            item (QAccordionItem): The item that was toggled.
            expanded (bool): Whether the item is checked (expanded).
        """
        self._scroll_layout.setStretchFactor(item, 1 if expanded else 0)

    def removeAccordionItem(self, item: QAccordionItem) -> None:
        """Removes an accordion item.

        Args:
            item (QAccordionItem): Accordion item to remove.
        """
        self._scroll_layout.removeWidget(item)
        self._items.remove(item)

    def item(self, name: str) -> Optional[QAccordionItem]:
        """Retrieves an accordion item by its name.

        Args:
            name (str): The name of the item to retrieve.

        Returns:
            Optional[QAccordionItem]: The item with the matching name, or None if not found.
        """
        for item in self._items:
            if item.objectName() == name:
                return item
        return None

    def items(self) -> typing.List[QAccordionItem]:
        """"""
        return self._items

    # --- Style Settings (Applied to ALL items) ---

    def setIconPosition(self, position: QAccordionHeader.IconPosition) -> None:
        """Changes the icon position of all items.

        Args:
            position (QAccordionHeader.IconPosition): New icon position.
        """
        self._items_icon_position = position
        for item in self._items:
            item.setIconPosition(position)

    def setIconStyle(self, style: QAccordionHeader.IndicatorStyle) -> None:
        """Changes the icon style of all items.

        Args:
            style (QAccordionHeader.IndicatorStyle): New icon style.
        """
        self._items_icon_style = style
        for item in self._items:
            item.setIconStyle(style)

    def setFlat(self, flat: bool) -> None:
        """Sets whether headers are flat or raised for all items.

        Args:
            flat (bool): True for flat headers, False for raised.
        """
        self._items_flat = flat
        for item in self._items:
            item.setFlat(flat)

    def setItemsAlignment(self, alignment: Qt.AlignmentFlag) -> None:
        """Sets the vertical alignment of the accordion items.

        Args:
            alignment (Qt.AlignmentFlag): The alignment (AlignTop, AlignVCenter, AlignBottom).
        """
        self._items_alignment = alignment
        self._scroll_layout.setAlignment(alignment)
        self._scroll_layout.update()

    def itemsAlignment(self) -> Qt.AlignmentFlag:
        """Returns the current vertical alignment of the accordion items.

        Returns:
            Qt.AlignmentFlag: The current alignment.
        """
        return self._items_alignment

    # --- Animation Settings (Applied to ALL items) ---

    def setAnimationEnabled(self, enabled: bool) -> None:
        """Enables or disables animations for all items.

        Args:
            enabled (bool): True to enable animations, False to disable.
        """
        self._animation_enabled = enabled
        for item in self._items:
            item.setAnimationEnabled(enabled)

    def isAnimationEnabled(self) -> bool:
        """Checks if animations are enabled by default.

        Returns:
            bool: True if animations are enabled, False otherwise.
        """
        return self._animation_enabled

    def setAnimationDuration(self, duration: int) -> None:
        """Sets the animation duration in milliseconds for all items.

        Args:
            duration (int): Duration in milliseconds (typical: 100-500).
        """
        self._animation_duration = duration
        for item in self._items:
            item.setAnimationDuration(duration)

    def animationDuration(self) -> int:
        """Returns the default animation duration.

        Returns:
            int: Animation duration in milliseconds.
        """
        return self._animation_duration

    def setAnimationEasing(self, easing: QEasingCurve.Type) -> None:
        """Sets the animation easing curve for all items.

        Args:
            easing (QEasingCurve.Type): The easing curve type.
        """
        self._animation_easing = easing
        for item in self._items:
            item.setAnimationEasing(easing)

    def animationEasing(self) -> QEasingCurve.Type:
        """Returns the default animation easing curve.

        Returns:
            QEasingCurve.Type: The easing curve type.
        """
        return self._animation_easing

    # --- Expand/Collapse Operations ---

    def expandAll(self, animated: bool = False) -> None:
        """Expands all accordion items.

        Args:
            animated (bool, optional): Override animation setting. If None, uses each item's setting. Defaults to None.
        """
        for item in self._items:
            item.setExpanded(True, animated=animated)

    def collapseAll(self, animated: bool = False) -> None:
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
