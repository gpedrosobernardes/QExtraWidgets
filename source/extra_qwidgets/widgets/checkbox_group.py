import typing

from PySide6.QtWidgets import QGridLayout, QWidget, QLabel, QCheckBox, QButtonGroup, QAbstractButton


class QCheckBoxGroup(QWidget):
    def __init__(self, label: QLabel):
        super().__init__()
        self.__layout = QGridLayout()
        self.__label = label
        self.__button_group = QButtonGroup()
        self.__button_group.setExclusive(True)
        self.__layout.addWidget(self.__label, 0, 0)
        self.setLayout(self.__layout)

    def add_checkbox(self, checkbox: QCheckBox):
        checkboxes = len(self.checkboxes())
        self.__layout.addWidget(checkbox, checkboxes, 1)
        self.__button_group.addButton(checkbox)

    def add_checkboxes(self, checkboxes: typing.Iterable[QCheckBox]):
        for c in checkboxes:
            self.add_checkbox(c)

    def get_checked(self) -> QAbstractButton:
        return self.__button_group.checkedButton()

    def checkboxes(self) -> list[QCheckBox]:
        return [w for w in self.children() if isinstance(w, QCheckBox)]