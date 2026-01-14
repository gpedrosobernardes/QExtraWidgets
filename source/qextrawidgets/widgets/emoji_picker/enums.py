from enum import IntEnum, StrEnum

from PySide6.QtGui import Qt


class QEmojiDataRole(IntEnum):
    AliasRole = Qt.ItemDataRole.UserRole + 1
    CategoryRole = Qt.ItemDataRole.UserRole + 2
    RecentRole = Qt.ItemDataRole.UserRole + 3
    FavoriteRole = Qt.ItemDataRole.UserRole + 4
    SkinTonesRole =  Qt.ItemDataRole.UserRole + 5
    HasSkinTonesRole = Qt.ItemDataRole.UserRole + 6


class EmojiSkinTone(StrEnum):
    """
    Modificadores de tom de pele (Fitzpatrick scale) suportados pelo Windows/Unicode.
    Herda de 'str' para facilitar a concatenação direta.
    """

    # Padrão (Geralmente Amarelo/Neutro) - Não adiciona nenhum código
    Default = ""

    # Tipo 1-2: Pele Clara
    Light = "1F3FB"  # 🏻

    # Tipo 3: Pele Morena Clara
    MediumLight = "1F3FC"  # 🏼

    # Tipo 4: Pele Morena
    Medium = "1F3FD"  # 🏽

    # Tipo 5: Pele Morena Escura
    MediumDark = "1F3FE"  # 🏾

    # Tipo 6: Pele Escura
    Dark = "1F3FF"  # 🏿
