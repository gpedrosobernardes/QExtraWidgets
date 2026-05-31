import logging
import time
import typing

from PySide6.QtCore import QPersistentModelIndex, QSize, Qt, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget

from qextrawidgets.core.utils.emojis import QEmojiImageProvider
from qextrawidgets.gui.proxys import QDecorationRoleProxyModel
from qextrawidgets.widgets.views.grid_icon_view import QGridIconView


class QEmojiView(QGridIconView):
    """
    A custom grid view designed specifically for displaying and selecting emojis.

    This class extends QGridIconView and automatically sets up a
    QDecorationRoleProxyModel. It handles dynamic emoji loading via an image
    provider (QEmojiImageProvider) or a custom pixmap getter.
    """

    def __init__(
        self,
        parent: typing.Optional[QWidget] = None,
        icon_pixmap_getter: typing.Optional[typing.Callable[[str], QPixmap]] = None,
    ):
        """
        Initialize the QEmojiView.

        Args:
            parent (Optional[QWidget]): The parent widget of the view. Defaults to None.
            icon_pixmap_getter (Optional[Callable[[str], QPixmap]]): A callable
                that takes an emoji string and returns a QPixmap. If None, a default
                QEmojiImageProvider is created.
        """
        super(QEmojiView, self).__init__(parent)
        self.setModel(QDecorationRoleProxyModel())

        if icon_pixmap_getter is None:
            self._emoji_image_provider = QEmojiImageProvider(32, self.devicePixelRatio())
            self.setIconPixmapGetter(self._emoji_image_provider.getPixmap)
        else:
            self._emoji_image_provider = None
            self.setIconPixmapGetter(icon_pixmap_getter)

        self.setup_connections()

    def setup_connections(self) -> None:
        """
        Connect signals to their respective slots for managing the image provider
        and delegation requests.
        """
        if self._emoji_image_provider is not None:
            self._emoji_image_provider.sourceChanged.connect(self._on_image_provider_settings_changed)
            self._emoji_image_provider.sizeChanged.connect(self._on_image_provider_settings_changed)
            self._emoji_image_provider.devicePixelRatioChanged.connect(self._on_image_provider_settings_changed)
            self.iconSizeChanged.connect(self._on_icon_size_changed)

        delegate = self.itemDelegate()
        delegate.requestImage.connect(self._on_request_image)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def setModel(self, model: QDecorationRoleProxyModel) -> None:
        """
        Set the decoration proxy model for the view.

        Args:
            model (QDecorationRoleProxyModel): The model to be set.
        """
        super(QEmojiView, self).setModel(model)

    def model(self) -> QDecorationRoleProxyModel:
        """
        Returns the current decoration proxy model.

        Returns:
            QDecorationRoleProxyModel: The proxy model cast to its correct type.
        """
        return typing.cast(QDecorationRoleProxyModel, super(QEmojiView, self).model())

    def setIconPixmapGetter(
        self,
        icon_pixmap_getter: typing.Callable[[str], QPixmap],
    ) -> None:
        """
        Sets the strategy for retrieving icon pixmaps.

        Args:
            icon_pixmap_getter (Callable[[str], QPixmap]): A callable that takes
                an emoji string and returns a QPixmap.
        """
        self._icon_pixmap_getter = icon_pixmap_getter

        delegate = self.itemDelegate()
        delegate.forceReloadAll()

    def iconPixmapGetter(self) -> typing.Callable[[str], QPixmap]:
        """
        Returns the current emoji pixmap getter function.

        Returns:
            Callable[[str], QPixmap]: A function that takes an emoji string and returns a QPixmap.
        """
        return self._icon_pixmap_getter

    def emojiImageProvider(self) -> typing.Optional[QEmojiImageProvider]:
        return self._emoji_image_provider

    # -------------------------------------------------------------------------
    # Internal Slots & Callbacks
    # -------------------------------------------------------------------------

    @Slot(QPersistentModelIndex)
    def _on_request_image(self, persistent_index: QPersistentModelIndex) -> None:
        """
        Loads the emoji image when requested by the delegate.

        Args:
            persistent_index (QPersistentModelIndex): The persistent index of the item needing an image.
        """
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}._on_request_image")

        start = time.perf_counter()

        if not persistent_index.isValid():
            return

        icon_pixmap_getter = self.iconPixmapGetter()

        if not icon_pixmap_getter:
            return

        emoji = persistent_index.data(Qt.ItemDataRole.EditRole)

        if emoji is None:
            return

        pixmap = icon_pixmap_getter(emoji)
        proxy = self.model()
        proxy.setData(persistent_index, pixmap, Qt.ItemDataRole.DecorationRole)

        end = time.perf_counter()
        logger.debug(f"Requested image for {emoji} in {end - start:.6f} seconds")

    @Slot(QSize)
    def _on_icon_size_changed(self, size: QSize) -> None:
        """
        Handles the iconSizeChanged signal to set a new size for the emoji icons.

        Args:
            size (QSize): The new width and height for the icons.
        """
        if self._emoji_image_provider is not None:
            self._emoji_image_provider.setSize(size.width())

    @Slot()
    def _on_image_provider_settings_changed(self) -> None:
        """
        Handles changes in the image provider's source, size, or pixel ratio.

        Forces a full reload of all items in the underlying grouped icon view delegate
        so the UI reflects the new image properties.
        """
        delegate = self.itemDelegate()
        delegate.forceReloadAll()