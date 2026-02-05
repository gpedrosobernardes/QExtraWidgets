from pathlib import Path

from PySide6.QtGui import QFontDatabase, QFont


class QEmojiFonts:
    """Utility class for loading and accessing emoji fonts."""

    TwemojiFontFamily = None

    @classmethod
    def loadTwemojiFont(cls) -> str:
        """Loads the bundled Twemoji font into the application font database.

        Returns:
            str: The loaded font family name.
        """
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
        """Returns a QFont object using the Twemoji font family.

        Returns:
            QFont: The Twemoji font.
        """
        return QFont(cls.loadTwemojiFont())
