from abc import ABCMeta

from PySide6.QtWidgets import QWidget

QtWidgetMeta = type(QWidget)


class QtABCMeta(ABCMeta, QtWidgetMeta):
    """Metaclass que herda de ABCMeta e da metaclass de QWidget."""
    pass