from PySide6.QtGui import QPainter, Qt, QImage
from PySide6.QtWidgets import QApplication


def is_dark_mode() -> bool:
    style_hints = QApplication.styleHints()
    color_scheme = style_hints.colorScheme()
    return color_scheme.value == 2
