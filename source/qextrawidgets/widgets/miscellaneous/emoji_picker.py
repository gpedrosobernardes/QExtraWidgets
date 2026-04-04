import logging
import random
import typing
from enum import Enum
from functools import lru_cache

from PySide6.QtGui import QPixmap, Qt, QFont, QIcon
from emoji_data_python import EmojiChar, emoji_data

from qextrawidgets.core.utils import QTwemojiImageProvider, QIconGenerator
from qextrawidgets.gui.items.icon_item import QIconItem
from qextrawidgets.gui.models.icon_picker_model import QIconPickerModel
from qextrawidgets.widgets.miscellaneous.icon_picker import QIconPicker


class EmojiSkinTone(str, Enum):
    """Skin tone modifiers (Fitzpatrick scale) supported by Unicode.

    Inherits from 'str' to facilitate direct concatenation with base emojis.

    Attributes:
        Default: Default skin tone (usually yellow/neutral). No modifier.
        Light: Type 1-2: Light skin tone.
        MediumLight: Type 3: Medium-light skin tone.
        Medium: Type 4: Medium skin tone.
        MediumDark: Type 5: Medium-dark skin tone.
        Dark: Type 6: Dark skin tone.
    """

    # Default (Generally Yellow/Neutral) - Adds no code
    Default = ""

    # Type 1-2: Light Skin
    Light = "1F3FB"

    # Type 3: Medium-Light Skin
    MediumLight = "1F3FC"

    # Type 4: Medium Skin
    Medium = "1F3FD"

    # Type 5: Medium-Dark Skin
    MediumDark = "1F3FE"

    # Type 6: Dark Skin
    Dark = "1F3FF"


@lru_cache(maxsize=None)
def _find_emoji_by_char(char: str) -> typing.Optional[EmojiChar]:
    """
    Find an EmojiChar object by its character string.
    Cached for performance.
    """
    return next((e for e in emoji_data if e.char == char), None)

def support_skin_tones(char: EmojiChar) -> bool:
    """
    Checks if the specified EmojiChar supports skin tones.

    Args:
        char: The EmojiChar instance to check.

    Returns:
        If it supports skin tones, returns True.
    """
    if char.skin_variations:
        return all(skin_tone in char.skin_variations for skin_tone in EmojiSkinTone if skin_tone != "")

    return False


class QEmojiPicker(QIconPicker):
    def __init__(self,
                 parent = None,
                 model: typing.Optional[QIconPickerModel] = None,
                 icon_label_size: int = 32,
                 icon_pixmap_getter: typing.Callable[[QIconItem], QPixmap] = None):
        """
        Initialize the QEmojiPicker class.
        Fill the color selector with a random emoji with all the skin tones supported.

        Args:
            parent (QWidget, optional): The parent widget.
            model (QIconPickerModel, optional): The QIconPickerModel instance. Uses a populated QIconPickerModel with emojis if None.
            icon_label_size (int, optional): The size of the emoji label. Defaults to 32.
        """
        if model is None:
            model = QIconPickerModel(QIconPickerModel.PopulateSource.Emojis)

        if icon_pixmap_getter is None:
            icon_pixmap_getter = self.emojiPixmapGetter

        skin_tones = list(EmojiSkinTone)

        emojis_with_color = [emoji_char.char for emoji_char in emoji_data if support_skin_tones(emoji_char)]
        random_color_emoji = random.choice(emojis_with_color)

        super().__init__(parent, model, icon_label_size, icon_pixmap_getter, ":{alias}:")

        for color_modifier in skin_tones:
            icon_item = QIconItem(random_color_emoji, True, None, color_modifier)
            self.addColorOption(icon_item)

    def emojiPixmapGetter(self, icon: QIconItem) -> QPixmap:
        """
        Helper emoji pixmap getter based on read emoji icons from local source.

        Args:
            icon: The QIconItem instance which have the emoji.

        Returns:
            Emoji pixmap getter function.
        """
        emoji = self.resolveEmojiColorByIcon(icon)
        if emoji is None:
            return QPixmap()

        return QTwemojiImageProvider.getPixmap(emoji, 0, self.view().iconSize().height())

    def fontEmojiPixmapGetter(self, font: typing.Union[str, QFont], icon: QIconItem) -> QPixmap:
        """
        Helper emoji pixmap getter based on extract emoji icons from specified font.

        Args:
            font: The source emoji font.
            icon: The QIconItem instance which have the emoji.

        Returns:
            Emoji pixmap getter function.
        """
        if isinstance(font, QFont):
            emoji_font = font
        else:
            emoji_font = QFont(font)

        emoji = self.resolveEmojiColorByIcon(icon)
        if emoji is None:
            return QPixmap()

        return QIconGenerator.charToPixmap(emoji, self.view().iconSize(), emoji_font)

    def resolveEmojiColorByIcon(self, icon: QIconItem) -> str:
        """
        Apply the skin tone color to the current emoji of the icon.

        Args:
            icon: The QIconItem instance.

        Returns:
            The colored emoji.
        """
        return self.resolveEmojiColor(icon.data(Qt.ItemDataRole.EditRole), icon.data(QIconItem.QIconItemDataRole.ColorModifierRole))

    def resolveEmojiColor(self, emoji: str, color_modifier: str) -> str:
        """
        Apply the skin tone color to an emoji.

        Args:
            emoji: Emoji string.
            color_modifier: Emoji skin tone.

        Returns:
            The colored emoji.
        """
        emoji_char = _find_emoji_by_char(emoji)
        if emoji_char is None:
            return ""

        if color_modifier:
            color_emoji = emoji_char.skin_variations.get(color_modifier)
            if color_emoji is None:
                logging.debug(f"Color {color_modifier} not found for emoji {emoji}")
            else:
                return color_emoji.char

        return emoji


