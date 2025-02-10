import typing

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QWidget, QLabel, QCheckBox


class QCheckBoxGroup(QWidget):
    def __init__(self, label: QLabel):
        super().__init__()
        self.__layout = QGridLayout()
        self.__label = label
        self.__checkboxes = {}
        self.__current = None
        self.__current_name = None
        self.__layout.addWidget(self.__label, 0, 0)
        self.setLayout(self.__layout)

    def add_checkbox(self, name: str, checkbox: QCheckBox):
        checkbox.checkStateChanged.connect(
            lambda check_state: self.__checkbox_checked(name, checkbox, check_state)
        )
        self.__layout.addWidget(checkbox, len(self.__checkboxes), 1)
        self.__checkboxes[name] = checkbox

    def __checkbox_checked(self, name: str, checkbox: QCheckBox, check_state: int):
        if check_state == Qt.CheckState.Checked:
            self.__current, self.__current_name = checkbox, name
            for checkbox_2 in self.__checkboxes.values():
                checkbox_2.setChecked(checkbox_2 == checkbox)
        elif name == self.__current_name:
            self.__current, self.__current_name = None, None

    def get_current_name(self) -> str:
        return self.__current_name

    def get_checkbox(self, name: str) -> typing.Optional[QCheckBox]:
        return self.__checkboxes.get(name)
