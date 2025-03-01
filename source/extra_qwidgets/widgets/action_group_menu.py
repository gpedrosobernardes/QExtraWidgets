from PySide6.QtGui import QActionGroup, QAction
from PySide6.QtWidgets import QMenu, QWidget


class QActionMenuGroup(QMenu):
    def __init__(self, text: str, parent: QWidget):
        super().__init__(text, parent)
        self.__action_group = QActionGroup(parent)
        self.__action_group.setExclusive(True)

    def addAction(self, action: QAction):
        super().addAction(action)
        self.__action_group.addAction(action)
        action.setCheckable(True)

    def addActions(self, actions):
        super().addActions(actions)
        for a in actions:
            self.__action_group.addAction(a)
            a.setCheckable(True)