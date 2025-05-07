from PySide6.QtWidgets import QGridLayout, QWidget, QLabel, QCheckBox

from extra_qwidgets.widgets.checkbox_group import QCheckBoxGroup


class QCheckBoxes(QWidget, QCheckBoxGroup):
    def __init__(self, label: QLabel):
        """
        A widget group of checkboxes with a label.
        :param label: QLabel
        """
        super().__init__()
        QCheckBoxGroup.__init__(self)
        self.__layout = QGridLayout()
        self.__label = label
        self.__layout.addWidget(self.__label, 0, 0)
        self.setLayout(self.__layout)

    def addCheckbox(self, checkbox: QCheckBox):
        """
        Adds a checkbox to the widget.
        :param checkbox: QCheckBox
        :return: None
        """
        self.__layout.addWidget(checkbox, len(self.checkboxes()), 1)
        super().addCheckbox(checkbox)

    def removeCheckbox(self, checkbox: QCheckBox):
        """
        Removes a checkbox from the widget.
        :param checkbox: QCheckBox
        :return: None
        """
        self.__layout.removeWidget(checkbox)
        super().removeCheckbox(checkbox)
