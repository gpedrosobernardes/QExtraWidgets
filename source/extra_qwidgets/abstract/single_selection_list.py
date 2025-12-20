from abc import abstractmethod, ABC
from typing import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QListWidget, QAbstractButton, QWidget

from extra_qwidgets.abstract.metaclass import QtABCMeta


class AbstractSingleSelectionList(QWidget, ABC, metaclass=QtABCMeta):
    def __init__(self):
        super().__init__()
        self.__to_select_list = self._new_list_widget()
        self.__selected_list = self._new_list_widget()
        self._select_button = self._new_tool_button("fa6s.angle-right")
        self._select_all_button = self._new_tool_button("fa6s.angles-right")
        self._deselect_button = self._new_tool_button("fa6s.angle-left")
        self._deselect_all_button = self._new_tool_button("fa6s.angles-left")
        buttons_layout = QVBoxLayout()
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.__to_select_list)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.__selected_list)
        for button in (self._select_button, self._select_all_button, self._deselect_button, self._deselect_all_button):
            buttons_layout.addWidget(button)
        self._select_button.clicked.connect(self.__select)
        self._deselect_button.clicked.connect(self.__deselect)
        self._select_all_button.clicked.connect(lambda: self.exchangeSelectedItems(self.getToSelectContent()))
        self._deselect_all_button.clicked.connect(lambda: self.exchangeToSelectItems(self.getToSelectContent()))
        self.setLayout(main_layout)

    @abstractmethod
    def _new_tool_button(self, icon: str) -> QAbstractButton:
        pass

    @abstractmethod
    def _new_list_widget(self) -> QListWidget:
        pass

    def __select(self):
        selected_items = self.__to_select_list.selectedItems()
        self.exchangeSelectedItems([item.text() for item in selected_items])

    def __deselect(self):
        selected_items = self.__selected_list.selectedItems()
        self.exchangeToSelectItems([item.text() for item in selected_items])

    def getSelectedContent(self) -> list[str]:
        return [self.__selected_list.item(i).text() for i in range(self.__selected_list.count())]

    def getToSelectContent(self) -> list[str]:
        return [self.__to_select_list.item(i).text() for i in range(self.__to_select_list.count())]

    def addToSelectItems(self, items: Sequence[str]):
        self.__to_select_list.addItems(items)

    def addSelectedItems(self, items: Sequence[str]):
        self.__selected_list.addItems(items)

    def removeToSelectItems(self, items: Sequence[str]):
        for item in items:
            item = self.__to_select_list.findItems(item, Qt.MatchFlag.MatchExactly)[0]
            self.__to_select_list.takeItem(self.__to_select_list.row(item))

    def removeSelectedItems(self, items: Sequence[str]):
        for item in items:
            item = self.__selected_list.findItems(item, Qt.MatchFlag.MatchExactly)[0]
            self.__selected_list.takeItem(self.__selected_list.row(item))

    def exchangeSelectedItems(self, items: Sequence[str]):
        self.__selected_list.addItems(items)
        self.removeToSelectItems(items)

    def exchangeToSelectItems(self, items: Sequence[str]):
        self.__to_select_list.addItems(items)
        self.removeSelectedItems(items)

    def clearToSelect(self):
        self.__to_select_list.clear()

    def clearSelected(self):
        self.__selected_list.clear()