from functools import partial

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton,
                               QButtonGroup, QSpinBox)

from qextrawidgets.gui.icons.theme_responsive_icon import QThemeResponsiveIcon


class QPager(QWidget):
    """Pagination component with a sliding window of buttons and in-place editing.

    Signals:
        currentPageChanged (int): Emitted when the current page changes.
    """

    # Public signals
    currentPageChanged = Signal(int)

    def __init__(self, parent: QWidget = None) -> None:
        """Initializes the pager widget.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)

        # --- Data Variables ---
        self._total_pages = 1
        self._current_page = 1
        self._max_visible_buttons = 5

        # --- UI and Layout Configuration ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Group for visual exclusivity
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)

        # List to track dynamic widgets
        self._page_widgets = []

        # 1. Navigation Buttons
        self._btn_first = self._create_nav_button(QThemeResponsiveIcon.fromAwesome("fa6s.backward-step"))
        self._btn_prev = self._create_nav_button(QThemeResponsiveIcon.fromAwesome("fa6s.angle-left"))
        self._btn_next = self._create_nav_button(QThemeResponsiveIcon.fromAwesome("fa6s.angle-right"))
        self._btn_last = self._create_nav_button(QThemeResponsiveIcon.fromAwesome("fa6s.forward-step"))

        # 2. Layout for numbers (where the magic happens)
        self._numbers_layout = QHBoxLayout()
        self._numbers_layout.setContentsMargins(0, 0, 0, 0)
        self._numbers_layout.setSpacing(2)

        # 3. Add to main layout
        main_layout.addWidget(self._btn_first)
        main_layout.addWidget(self._btn_prev)
        main_layout.addLayout(self._numbers_layout)
        main_layout.addWidget(self._btn_next)
        main_layout.addWidget(self._btn_last)

        # --- Connections ---
        self._setup_connections()

        # Initialization
        self._update_view()

    # --- Internal Creation Methods ---

    @staticmethod
    def _create_nav_button(icon: QIcon) -> QPushButton:
        """Creates a navigation button (first, prev, next, last).

        Args:
            icon (QIcon): Button icon.

        Returns:
            QPushButton: The created button.
        """
        btn = QPushButton()
        btn.setIcon(icon)
        btn.setFixedSize(30, 30)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    @staticmethod
    def _create_page_button(text: str) -> QPushButton:
        """Creates a button representing a page number.

        Args:
            text (str): Button text (page number).

        Returns:
            QPushButton: The created page button.
        """
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setFixedSize(30, 30)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def _create_editor(self) -> QSpinBox:
        """Creates the numeric input that replaces the button for in-place editing.

        Returns:
            QSpinBox: The created spin box editor.
        """
        spin = QSpinBox()
        spin.setFixedSize(60, 30)  # Slightly wider to fit large numbers
        spin.setFrame(False)  # No border to look integrated
        spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)  # Remove up/down arrows
        spin.setRange(1, self._total_pages)
        spin.setValue(self._current_page)
        return spin

    def _setup_connections(self) -> None:
        """Sets up signals and slots connections."""
        self._btn_first.clicked.connect(lambda: self.setCurrentPage(1))
        self._btn_prev.clicked.connect(lambda: self.setCurrentPage(self._current_page - 1))
        self._btn_next.clicked.connect(lambda: self.setCurrentPage(self._current_page + 1))
        self._btn_last.clicked.connect(lambda: self.setCurrentPage(self._total_pages))

    # --- Visualization and Editing Logic ---

    def _update_view(self) -> None:
        """Rebuilds the number bar based on current state."""

        # 1. Calculate Sliding Window
        half = self._max_visible_buttons // 2
        start_page = max(1, self._current_page - half)
        end_page = min(self._total_pages, start_page + self._max_visible_buttons - 1)

        if end_page - start_page + 1 < self._max_visible_buttons:
            start_page = max(1, end_page - self._max_visible_buttons + 1)

        # 2. Total Cleanup of numeric area
        while self._numbers_layout.count():
            item = self._numbers_layout.takeAt(0)
            widget = item.widget()
            if widget:
                if isinstance(widget, QPushButton):
                    self._button_group.removeButton(widget)
                widget.deleteLater()
        self._page_widgets.clear()

        # 3. Button Construction
        for page_num in range(start_page, end_page + 1):
            btn = self._create_page_button(str(page_num))
            self._button_group.addButton(btn)

            if page_num == self._current_page:
                btn.setChecked(True)
                # The current button not only navigates, it opens editing
                btn.setToolTip(self.tr("Click to type page"))
                btn.clicked.connect(partial(self.__on_edit_requested, btn))
            else:
                # Normal buttons just navigate
                btn.clicked.connect(partial(self.setCurrentPage, page_num))

            self._numbers_layout.addWidget(btn)
            self._page_widgets.append(btn)

        # 4. Navigation States
        self._btn_first.setEnabled(self._current_page > 1)
        self._btn_prev.setEnabled(self._current_page > 1)
        self._btn_next.setEnabled(self._current_page < self._total_pages)
        self._btn_last.setEnabled(self._current_page < self._total_pages)

    def __on_edit_requested(self, button_sender: QPushButton) -> None:
        """Slot called when the user clicks on the current page to start editing.

        Replaces the button with a SpinBox.

        Args:
            button_sender (QPushButton): The button that was clicked.
        """
        # 1. Identify position in layout
        index = self._numbers_layout.indexOf(button_sender)
        if index == -1: return

        # 2. Create and configure editor
        spin = self._create_editor()

        # 3. Replace in layout (Swap)
        # We remove the button from the layout and hide it (don't delete yet to avoid crash in active slots)
        item = self._numbers_layout.takeAt(index)
        button_sender.hide()
        self._button_group.removeButton(button_sender)  # Important not to bug the group

        self._numbers_layout.insertWidget(index, spin)
        spin.setFocus()
        spin.selectAll()

        # 4. Editor Connections
        # If Enter is pressed or focus is lost, confirms editing
        spin.editingFinished.connect(lambda: self.setCurrentPage(spin.value()))

        # If focus is lost without pressing enter, we force update to restore the button
        # (This is done implicitly because setCurrentPage calls _update_view)

    # --- Public API ---

    def setTotalPages(self, total: int) -> None:
        """Sets the total number of pages.

        Args:
            total (int): Total page count.
        """
        if total < 1: total = 1
        self._total_pages = total
        if self._current_page > total:
            self.setCurrentPage(total)
        else:
            self._update_view()

    def totalPages(self) -> int:
        """Returns the total number of pages.

        Returns:
            int: Total page count.
        """
        return self._total_pages

    def setVisibleButtonCount(self, count: int) -> None:
        """Sets how many page buttons are visible at once.

        Args:
            count (int): Maximum number of visible page buttons.
        """
        if count < 1: count = 1
        self._max_visible_buttons = count
        self._update_view()

    def visibleButtonCount(self) -> int:
        """Returns the maximum number of visible page buttons.

        Returns:
            int: Visible button count.
        """
        return self._max_visible_buttons

    def setCurrentPage(self, page: int) -> None:
        """Sets the current page index.

        Args:
            page (int): Page index to set.
        """
        if page < 1: page = 1
        if page > self._total_pages: page = self._total_pages

        # Updates state
        self._current_page = page

        # Emits signal only if changed
        # But ALWAYS calls _update_view to ensure SpinBox
        # (if it exists) is destroyed and the button returns.
        self._update_view()
        self.currentPageChanged.emit(page)

    def currentPage(self) -> int:
        """Returns the current page index.

        Returns:
            int: Current page.
        """
        return self._current_page
