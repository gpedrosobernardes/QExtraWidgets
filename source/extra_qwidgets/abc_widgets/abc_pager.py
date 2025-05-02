import typing
from abc import abstractmethod

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QAbstractButton, QWidget, QHBoxLayout

from extra_qwidgets.abc_widgets.abc_meta import QtABCMeta


# noinspection PyPep8Naming
class ABCPager(QWidget, metaclass=QtABCMeta):
    currentPageChanged = Signal(int)
    pagePressed = Signal(int)
    previousPagePressed = Signal()
    nextPagePressed = Signal()
    firstPagePressed = Signal()
    lastPagePressed = Signal()

    def __init__(self, page_count: int = 10, current_page: int = 1, visible_button_count: int = 5):
        super().__init__()
        self._page_count = page_count
        self._current_page = current_page
        self._visible_button_count = visible_button_count
        self._first_page_button = self._new_icon_button("fa6s.angles-left")
        self._prev_page_button = self._new_icon_button("fa6s.angle-left")
        self._next_page_button = self._new_icon_button("fa6s.angle-right")
        self._last_page_button = self._new_icon_button("fa6s.angles-right")
        self._buttons: typing.List[QAbstractButton] = []
        self._layout = QHBoxLayout(self)
        self._layout.addWidget(self._first_page_button)
        self._layout.addWidget(self._prev_page_button)
        self._layout.addWidget(self._next_page_button)
        self._layout.addWidget(self._last_page_button)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        self._setup_buttons()
        self._setup_binds()

    def _setup_binds(self):
        self.pagePressed.connect(self.setCurrentPage)
        self._first_page_button.clicked.connect(self.firstPagePressed.emit)
        self._first_page_button.clicked.connect(lambda: self.setCurrentPage(1))
        self._prev_page_button.clicked.connect(self.previousPagePressed.emit)
        self._prev_page_button.clicked.connect(lambda: self.setCurrentPage(self._current_page - 1))
        self._next_page_button.clicked.connect(self.nextPagePressed.emit)
        self._next_page_button.clicked.connect(lambda: self.setCurrentPage(self._current_page + 1))
        self._last_page_button.clicked.connect(self.lastPagePressed.emit)
        self._last_page_button.clicked.connect(lambda: self.setCurrentPage(self._page_count))

    def _setup_buttons(self):
        for i in range(self._get_real_visible_button_count()):
            self._add_button(i + 1)

    def _update_buttons_text(self):
        real_visible_button_count = self._get_real_visible_button_count()
        if self._current_page + real_visible_button_count - 1 <= self._page_count:
            first_button_page = self._current_page
        else:
            first_button_page = self._page_count - real_visible_button_count + 1
        for i in range(real_visible_button_count):
            page = first_button_page + i
            btn = self._buttons[i]
            btn.setChecked(page == self._current_page)
            btn.setText(str(page))

    def _get_real_visible_button_count(self):
        return min(self._visible_button_count, self._page_count)

    def _update_visible_buttons(self):
        max_buttons = self._get_real_visible_button_count()
        buttons = len(self._buttons)
        if buttons > max_buttons:
            for i in range(buttons - max_buttons):
                self._remove_button(i)
        elif buttons < max_buttons:
            for i in range(buttons, max_buttons):
                self._add_button(self._current_page + i + 1)

    def _remove_button(self, index: int):
        btn = self._buttons.pop(index)
        self._layout.removeWidget(btn)
        btn.deleteLater()

    def _add_button(self, page: int):
        button = self._new_page_button()
        button.setCheckable(True)
        button.setChecked(page == self._current_page)
        button.setText(str(page))
        button.clicked.connect(lambda: self.pagePressed.emit(int(button.text())))
        self._layout.insertWidget(2 + len(self._buttons), button)
        self._buttons.append(button)

    def getShortcutButtonsVisible(self) -> bool:
        return self._first_page_button.isVisible() and self._last_page_button.isVisible()

    def setShortcutButtonsVisible(self, visible: bool):
        self._first_page_button.setVisible(visible)
        self._last_page_button.setVisible(visible)

    def getCurrentPage(self) -> int:
        return self._current_page

    def setCurrentPage(self, page: int):
        if page >= self._page_count:
            page = self._page_count
        elif page <= 1:
            page = 1
        self._current_page = page
        self._update_buttons_text()
        self.currentPageChanged.emit(page)

    def getVisibleButtonCount(self) -> int:
        return self._visible_button_count

    def setVisibleButtonCount(self, count: int):
        self._visible_button_count = count
        self._update_visible_buttons()
        self._update_buttons_text()

    def getPageCount(self) -> int:
        return self._page_count

    def setPageCount(self, page_count: int):
        self._page_count = page_count
        if self._current_page > page_count:
            self._current_page = page_count
        self._update_visible_buttons()
        self._update_buttons_text()

    @abstractmethod
    def _new_page_button(self) -> QAbstractButton:
        pass

    @abstractmethod
    def _new_icon_button(self, icon: str) -> QAbstractButton:
        pass
