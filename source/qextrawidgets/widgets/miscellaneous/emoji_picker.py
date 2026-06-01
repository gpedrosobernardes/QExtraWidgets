import random
import typing

from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap, QScreen

from qextrawidgets.core.utils.emojis.emoji_image_provider import QEmojiImageProvider
from qextrawidgets.core.utils.emojis.emoji_utils import EmojiSkinTone, QEmojiUtils
from qextrawidgets.gui.items.icon_item import QIconItem
from qextrawidgets.gui.models.icon_picker_model import QIconPickerModel
from qextrawidgets.widgets.delegates import QGroupedIconDelegate
from qextrawidgets.widgets.miscellaneous.icon_picker import QIconPicker


class QEmojiPicker(QIconPicker):
    """A widget for picking emojis, supporting different skin tones and dynamic scaling.

    Inherits from QIconPicker to provide a specialized grid for emoji selection.
    """

    def __init__(self,
                 parent=None,
                 model: typing.Optional[QIconPickerModel] = None,
                 icon_label_size: int = 32,
                 icon_pixmap_getter: typing.Optional[typing.Callable[[QIconItem, QSize, float], QPixmap]] = None):
        """Initializes the QEmojiPicker class.

        Fills the color selector with a random emoji demonstrating all supported skin tones.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
            model (QIconPickerModel, optional): The model containing icon data. If None,
                a populated QIconPickerModel with emojis will be instantiated. Defaults to None.
            icon_label_size (int, optional): The size of the emoji label in pixels. Defaults to 32.
            icon_pixmap_getter (Callable[[QIconItem], QPixmap], optional): Custom callback to
                retrieve pixmaps. If None, the default QEmojiImageProvider is used. Defaults to None.
        """
        self._emoji_image_provider = None

        if model is None:
            model = QIconPickerModel(QIconPickerModel.PopulateSource.Emojis)

        skin_tones = list(EmojiSkinTone)

        emojis_with_color = QEmojiUtils.emojisWithSkinTones()
        random_color_emoji = random.choice(emojis_with_color)

        super().__init__(parent, model, icon_label_size, None, ":{alias}:")

        if icon_pixmap_getter is None:
            self._emoji_image_provider = QEmojiImageProvider()
            self._emoji_image_provider.sourceChanged.connect(self._on_image_provider_settings_changed)

            self.setIconPixmapGetter(self._emoji_image_provider.getPixmapFromIconItem)
        else:
            self._emoji_image_provider = None
            self.setIconPixmapGetter(icon_pixmap_getter)

        for color_modifier in skin_tones:
            icon_item = QIconItem(random_color_emoji, True, None, color_modifier)
            self.addColorOption(icon_item)

    def _on_image_provider_settings_changed(self):
        """Handles changes in the image provider's source, size, or pixel ratio.

        Forces a full reload of all items in the underlying grouped icon view delegate
        so the UI reflects the new image properties.
        """
        delegate: QGroupedIconDelegate = self._grouped_icon_view.itemDelegate()
        delegate.forceReloadAll()

    def getEmojiImageProvider(self) -> typing.Optional[QEmojiImageProvider]:
        """Retrieves the current emoji image provider instance.

        Returns:
            typing.Optional[QEmojiImageProvider]: The internal QEmojiImageProvider if using
                the default pixmap getter, or None if a custom getter was provided.
        """
        return self._emoji_image_provider