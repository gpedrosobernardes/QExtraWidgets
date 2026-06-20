import random
import typing

from PySide6.QtCore import QSize, Slot, QPersistentModelIndex, QModelIndex, QUrlQuery
from PySide6.QtGui import QPixmap, QStandardItem, Qt

from qextrawidgets.core.runnables.emoji_image_provider import QEmojiImageProvider
from qextrawidgets.core.utils.emojis.emoji_utils import EmojiSkinVariations, QEmojiUtils
from qextrawidgets.core.utils.system_utils import debug
from qextrawidgets.gui.models.emoji_picker_model import QEmojiPickerModel
from qextrawidgets.widgets.delegates import QGroupedIconDelegate
from qextrawidgets.widgets.miscellaneous.icon_picker import QIconPicker


class QEmojiPicker(QIconPicker):
    """A widget for picking emojis, supporting different skin tones and dynamic scaling.

    Inherits from QIconPicker to provide a specialized grid for emoji selection.
    """

    def __init__(self,
                 model: QEmojiPickerModel,
                 parent=None,
                 icon_label_size: int = 32):
        super().__init__(QEmojiImageProvider, model, parent, icon_label_size, ":{alias}:")

        skin_varied_emojis = list(QEmojiUtils.skinVariedEmojis())
        emoji_char = random.choice(skin_varied_emojis)

        # for skin_variation in [None] + list(EmojiSkinVariations):
        #     skin_varied_emoji_char = QEmojiUtils.applySkinVariation(emoji_char, skin_variation)
        #     icon_item = QStandardItem()
        #     icon_item.setData(skin_varied_emoji_char, Qt.ItemDataRole.EditRole)
        #     icon_item.setData(skin_variation, Qt.ItemDataRole.UserRole)
        #     self.addColorOption(icon_item)

    def _build_url_query(self, index: typing.Union[QPersistentModelIndex, QModelIndex], size: QSize) -> QUrlQuery:
        emoji_char = index.data(Qt.ItemDataRole.EditRole)

        url_query = QUrlQuery()
        url_query.addQueryItem("emoji", emoji_char.char)
        url_query.addQueryItem("size", str(size.width()))
        url_query.addQueryItem("font_family", "Twemoji")
        return url_query

    @Slot(QStandardItem)
    def _on_set_color_modifier(self, icon_item: QStandardItem) -> None:
        """Updates the skin tone of the emojis.

        Args:
            icon_item (QIconItem): QIconItem instance representing the color_modifier.
        """
        skin_variation = icon_item.data(Qt.ItemDataRole.UserRole)
        if isinstance(self._model, QEmojiPickerModel):
            self._model.setSkinVariation(skin_variation)