from pathlib import Path

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication


def is_dark_mode() -> bool:
    style_hints = QApplication.styleHints()
    color_scheme = style_hints.colorScheme()
    return color_scheme.value == 2

# https://github.com/googlefonts/color-fonts/tree/main/fonts


class QEmojiFonts:

    TwemojiFontFamily = None

    @classmethod
    def loadTwemojiFont(cls) -> str:

        if not cls.TwemojiFontFamily:
            root_folder_path = Path(__file__).parent
            fonts_folder_path = root_folder_path / "fonts"
            file_path = fonts_folder_path / "Twemoji-17.0.2.ttf"

            id_ = QFontDatabase.addApplicationFont(str(file_path))
            family = QFontDatabase.applicationFontFamilies(id_)[0]

            cls.TwemojiFontFamily = family

        return cls.TwemojiFontFamily

    @classmethod
    def twemojiFont(cls) -> QFont:
        return QFont(cls.loadTwemojiFont())