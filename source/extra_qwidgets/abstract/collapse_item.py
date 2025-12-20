import typing
from abc import abstractmethod, ABCMeta, ABC

import qtawesome as qta
from PySide6.QtCore import QObject
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QAbstractButton

from extra_qwidgets.abstract.metaclass import QtABCMeta


# noinspection PyPep8Naming
class AbstractCollapseItem(QObject, ABC, metaclass=QtABCMeta):
    def __init__(self, title: str, child: QWidget, collapsed: bool = False, name: typing.Optional[str] = None):
        """
        A collapsible group widget.
        :param title: str
        """
        super().__init__()
        if name:
            self.setObjectName(name)
        self.__collapsed = collapsed
        self._child = child
        self.__collapse_button = self._new_collapse_button()
        down_icon = qta.icon('fa6s.angle-down').pixmap(24, 24)
        up_icon = qta.icon('fa6s.angle-up').pixmap(24, 24)
        icon = QIcon()
        icon.addPixmap(up_icon, QIcon.Mode.Normal, QIcon.State.Off)
        icon.addPixmap(down_icon, QIcon.Mode.Normal, QIcon.State.On)
        self.__collapse_button.setIcon(icon)
        self.__collapse_button.setCheckable(True)
        self.__collapse_button.toggled.connect(lambda checked: self._child.setVisible(checked))
        self.__collapse_button.setChecked(not collapsed)
        self.__label = QLabel(title)
        self.__header_layout = QHBoxLayout()
        self.__header_layout.addWidget(self.__collapse_button)
        self.__header_layout.addWidget(self.__label, 1)
        self.__header_layout.setSpacing(10)

    def setCollapse(self, collapse: bool):
        """
        Sets if the widget is collapsed.
        :param collapse: bool
        :return: None
        """
        self.__collapse_button.setChecked(not collapse)

    def isCollapsed(self) -> bool:
        return self.__collapse_button.isChecked()

    @abstractmethod
    def _new_collapse_button(self) -> QAbstractButton:
        pass

    def header(self) -> QLabel:
        """
        Returns the header label.
        :return: QLabel
        """
        return self.__label

    def headerLayout(self) -> QHBoxLayout:
        return self.__header_layout

    def widget(self) -> QWidget:
        return self._child