import typing

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QPixmap, QPixmapCache
from PySide6.QtWidgets import QWidget
from emoji_data_python import EmojiChar

from qextrawidgets.core.utils.emojis import QEmojiPixmapCache
from qextrawidgets.gui.proxys.decoration_provider_proxy import QDecorationProviderProxy
from qextrawidgets.widgets.views.grid_icon_view import QGridIconView


class QEmojiView(QGridIconView):
    def __init__(
        self,
        emoji_font_family: str,
        parent: typing.Optional[QWidget] = None,
    ):
        super(QEmojiView, self).__init__(parent)
        model = QDecorationProviderProxy()
        model.setDecorationProvider(self._decoration_provider)
        self.setModel(model)
        self._emoji_font_family = emoji_font_family

    def setEmojiFontFamily(self, emoji_font_family: str):
        if self._emoji_font_family != emoji_font_family:
            self._emoji_font_family = emoji_font_family
            self.viewport().update()

    def _decoration_provider(self, index: QModelIndex) -> QPixmap:
        emoji_char: EmojiChar = index.data(Qt.ItemDataRole.EditRole)
        try:
            pixmap = QEmojiPixmapCache.getPixmap(self._emoji_font_family, emoji_char.unified)
        except KeyError:
            return None
        else:
            return pixmap

    def setModel(self, model: QDecorationProviderProxy):
        super(QEmojiView, self).setModel(model)

    def model(self) -> QDecorationProviderProxy:
        return typing.cast(QDecorationProviderProxy, super(QEmojiView, self).model())