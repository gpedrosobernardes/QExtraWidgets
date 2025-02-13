from typing import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QHBoxLayout

from extra_qwidgets.widgets.theme_responsive_button import QThemeResponsiveButton
from extra_qwidgets.utils import get_awesome_icon


class QSingleSelectionList(QWidget):
    def __init__(self):
        super().__init__()
        self.__to_select_list = QListWidget()
        self.__selected_list = QListWidget()

        self.__select_button = QThemeResponsiveButton()
        self.__select_button.setIcon(get_awesome_icon("angle-right"))

        self.__select_all_button = QThemeResponsiveButton()
        self.__select_all_button.setIcon(get_awesome_icon("angles-right"))

        self.__deselect_button = QThemeResponsiveButton()
        self.__deselect_button.setIcon(get_awesome_icon("angle-left"))

        self.__deselect_all_button = QThemeResponsiveButton()
        self.__deselect_all_button.setIcon(get_awesome_icon("angles-left"))

        buttons_layout = QVBoxLayout()
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.__to_select_list)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.__selected_list)

        for button in (self.__select_button, self.__select_all_button, self.__deselect_button, self.__deselect_all_button):
            button.setFlat(True)
            buttons_layout.addWidget(button)

        self.__select_button.clicked.connect(self.__select)
        self.__deselect_button.clicked.connect(self.__deselect)
        self.__select_all_button.clicked.connect(lambda: self.exchange_selected_items(self.get_to_select_content()))
        self.__deselect_all_button.clicked.connect(lambda: self.exchange_to_select_items(self.get_selected_content()))

        self.setLayout(main_layout)

    def __select(self):
        selected_items = self.__to_select_list.selectedItems()
        self.exchange_selected_items([item.text() for item in selected_items])

    def __deselect(self):
        selected_items = self.__selected_list.selectedItems()
        self.exchange_to_select_items([item.text() for item in selected_items])

    def to_select_list(self) -> QListWidget:
        return self.__to_select_list

    def selected_list(self) -> QListWidget:
        return self.__selected_list

    def get_selected_content(self) -> list[str]:
        return [self.__selected_list.item(i).text() for i in range(self.__selected_list.count())]

    def get_to_select_content(self) -> list[str]:
        return [self.__to_select_list.item(i).text() for i in range(self.__to_select_list.count())]

    def add_to_select_items(self, items: Sequence[str]):
        self.__to_select_list.addItems(items)

    def add_selected_items(self, items: Sequence[str]):
        self.__selected_list.addItems(items)

    def remove_to_select_items(self, items: Sequence[str]):
        for item in items:
            item = self.__to_select_list.findItems(item, Qt.MatchFlag.MatchExactly)[0]
            self.__to_select_list.takeItem(self.__to_select_list.row(item))

    def remove_selected_items(self, items: Sequence[str]):
        for item in items:
            item = self.__selected_list.findItems(item, Qt.MatchFlag.MatchExactly)[0]
            self.__selected_list.takeItem(self.__selected_list.row(item))

    def exchange_selected_items(self, items: Sequence[str]):
        self.__selected_list.addItems(items)
        self.remove_to_select_items(items)

    def exchange_to_select_items(self, items: Sequence[str]):
        self.__to_select_list.addItems(items)
        self.remove_selected_items(items)

    def clear_to_select(self):
        self.__to_select_list.clear()

    def clear_selected(self):
        self.__selected_list.clear()