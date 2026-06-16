import typing

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget
from emoji_data_python import EmojiChar

from qextrawidgets.core.utils.emojis.global_emoji_pixmap_cache import QGlobalEmojiPixmapCache
from qextrawidgets.gui.proxys.decoration_provider_proxy import QDecorationProviderProxy
from qextrawidgets.widgets.views.grid_icon_view import QGridIconView


class QEmojiView(QGridIconView):
    def __init__(
        self,
        font_family: str,
        parent: typing.Optional[QWidget] = None,
    ):
        super(QEmojiView, self).__init__(parent)
        model = QDecorationProviderProxy()
        model.setDecorationProvider(self._decoration_provider)
        self.setModel(model)
        self._emoji_pixmap_cache = QGlobalEmojiPixmapCache.ensureCache(font_family)

    def updateEmojiPixmapCache(self, font_family: str):
        self._emoji_pixmap_cache = QGlobalEmojiPixmapCache.ensureCache(font_family)

    def _decoration_provider(self, index: QModelIndex) -> QPixmap:
        emoji_char: EmojiChar = index.data(Qt.ItemDataRole.EditRole)
        try:
            pixmap = self._emoji_pixmap_cache.getPixmap(emoji_char.char)
        except KeyError:
            return None
        else:
            return pixmap

    def setModel(self, model: QDecorationProviderProxy):
        super(QEmojiView, self).setModel(model)

    def model(self) -> QDecorationProviderProxy:
        return typing.cast(QDecorationProviderProxy, super(QEmojiView, self).model())