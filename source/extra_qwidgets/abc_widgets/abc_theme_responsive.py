from abc import abstractmethod

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from extra_qwidgets.abc_widgets.abc_meta import QtABCMeta
from extra_qwidgets.utils import colorize_icon_by_theme


class ABCThemeResponsive(metaclass=QtABCMeta):
    def __init__(self, *args, **kwargs):
        self._bind_theme_change()

    def _bind_theme_change(self):
        QApplication.styleHints().colorSchemeChanged.connect(self._on_theme_change)

    def _on_theme_change(self):
        self.setIcon(colorize_icon_by_theme(self.icon()))

    @abstractmethod
    def setIcon(self, icon: QIcon):
        pass

    @abstractmethod
    def icon(self) -> QIcon:
        pass