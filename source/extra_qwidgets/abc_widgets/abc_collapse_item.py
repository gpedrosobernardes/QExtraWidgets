import typing
from abc import abstractmethod

import qtawesome
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QAbstractButton

from extra_qwidgets.abc_widgets.abc_meta import QtABCMeta


# noinspection PyPep8Naming
class ABCCollapseItem(QObject, metaclass=QtABCMeta):
    def __init__(self, title: str, child: QWidget, collapsed: bool = False, name: typing.Optional[str] = None):
        """
        A collapsible group widget.
        :param title: str
        """
        super().__init__()
        if name:
            self.setObjectName(name)
        self.__collapsed = collapsed
        self.__collapse_button = self._new_collapse_button()
        self.__collapse_button.setIcon(qtawesome.icon("fa6s.angle-down"))
        self.__collapse_button.clicked.connect(
            lambda: self.setCollapse(not self.__collapsed)
        )
        self.__label = QLabel(title)
        self.__header_layout = QHBoxLayout()
        self.__header_layout.addWidget(self.__collapse_button)
        self.__header_layout.addWidget(self.__label, 1)
        self.__header_layout.setSpacing(10)
        self._child = child
        self._set_collapsed(collapsed)

    def setCollapse(self, collapse: bool):
        """
        Sets if the widget is collapsed.
        :param collapse: bool
        :return: None
        """
        self.__collapsed = collapse
        self._set_collapsed(collapse)

    def _set_collapsed(self, collapse: bool):
        if collapse:
            self._child.hide()
            self.__collapse_button.setIcon(qtawesome.icon("fa6s.angle-up"))
        else:
            self._child.show()
            self.__collapse_button.setIcon(qtawesome.icon("fa6s.angle-down"))

    def isCollapsed(self) -> bool:
        return self.__collapsed

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