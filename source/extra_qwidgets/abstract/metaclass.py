from abc import ABCMeta
from PySide6 import Shiboken
from PySide6.QtCore import QObject


class QtABCMeta(type(QObject), ABCMeta):
    pass