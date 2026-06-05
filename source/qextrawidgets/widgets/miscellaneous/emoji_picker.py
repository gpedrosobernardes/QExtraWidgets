import random
import typing

from PySide6.QtCore import QSize, Slot
from PySide6.QtGui import QPixmap, QStandardItem, Qt

from qextrawidgets.core.utils.emojis.emoji_image_provider import QEmojiImageProvider
from qextrawidgets.core.utils.emojis.emoji_utils import EmojiSkinVariations, QEmojiUtils
from qextrawidgets.gui.models.emoji_picker_model import QEmojiPickerModel
from qextrawidgets.widgets.delegates import QGroupedIconDelegate
from qextrawidgets.widgets.miscellaneous.icon_picker import QIconPicker


class QEmojiPicker(QIconPicker):
    """A widget for picking emojis, supporting different skin tones and dynamic scaling.

    Inherits from QIconPicker to provide a specialized grid for emoji selection.
    """

    def __init__(self,
                 parent=None,
                 model: typing.Optional[QEmojiPickerModel] = None,
                 icon_label_size: int = 32,
                 icon_pixmap_getter: typing.Optional[typing.Callable[[QStandardItem, QSize, float], QPixmap]] = None):
        """Initializes the QEmojiPicker class.

        Fills the color selector with a random emoji demonstrating all supported skin tones.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
            model (QIconPickerModel, optional): The model containing icon data. If None,
                a populated QIconPickerModel with emojis will be instantiated. Defaults to None.
            icon_label_size (int, optional): The size of the emoji label in pixels. Defaults to 32.
            icon_pixmap_getter (Callable[[QIconItem, QSize, float], QPixmap], optional): Custom callback to
                retrieve pixmaps. If None, the default QEmojiImageProvider is used. Defaults to None.
        """
        self._emoji_image_provider = None

        if model is None:
            model = QEmojiPickerModel()

        super().__init__(parent, model, icon_label_size, None, ":{alias}:")

        if icon_pixmap_getter is None:
            self._emoji_image_provider = QEmojiImageProvider()
            self._emoji_image_provider.sourceChanged.connect(self._on_image_provider_settings_changed)

            self.setIconPixmapGetter(self._emoji_image_provider.getPixmapFromIconItem)
        else:
            self._emoji_image_provider = None
            self.setIconPixmapGetter(icon_pixmap_getter)

        skin_varied_emojis = list(QEmojiUtils.skinVariedEmojis())
        emoji_char = random.choice(skin_varied_emojis)

        for skin_variation in [None] + list(EmojiSkinVariations):
            skin_varied_emoji_char = QEmojiUtils.applySkinVariation(emoji_char, skin_variation)
            icon_item = QStandardItem()
            icon_item.setData(skin_varied_emoji_char, Qt.ItemDataRole.EditRole)
            icon_item.setData(skin_variation, Qt.ItemDataRole.UserRole)
            self.addColorOption(icon_item)

    def _on_image_provider_settings_changed(self):
        """Handles changes in the image provider's source, size, or pixel ratio.

        Forces a full reload of all items in the underlying grouped icon view delegate
        so the UI reflects the new image properties.
        """
        delegate: QGroupedIconDelegate = self._grouped_icon_view.itemDelegate()
        delegate.forceReloadAll()

    @Slot(QStandardItem)
    def _on_set_color_modifier(self, icon_item: QStandardItem) -> None:
        """Updates the skin tone of the emojis.

        Args:
            icon_item (QIconItem): QIconItem instance representing the color_modifier.
        """
        skin_variation = icon_item.data(Qt.ItemDataRole.UserRole)
        model = self.model()
        model.setSkinVariation(skin_variation)

    def getEmojiImageProvider(self) -> typing.Optional[QEmojiImageProvider]:
        """Retrieves the current emoji image provider instance.

        Returns:
            typing.Optional[QEmojiImageProvider]: The internal QEmojiImageProvider if using
                the default pixmap getter, or None if a custom getter was provided.
        """
        return self._emoji_image_provider

    def model(self) -> QEmojiPickerModel:
        """Retrieves the current model instance.
        Returns:
        """
        return self._model