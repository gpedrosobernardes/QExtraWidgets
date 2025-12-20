from abc import abstractmethod, ABC

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from extra_qwidgets.abstract.metaclass import QtABCMeta
from extra_qwidgets.utils import colorize_icon_by_theme


class AbstractThemeResponsive(ABC, metaclass=QtABCMeta):
    def __init__(self, **_):
        super().__init__()
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