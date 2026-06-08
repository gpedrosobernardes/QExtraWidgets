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
    A grid view designed specifically for displaying and selecting emojis.

    Extends :class:`QGridIconView` and wires together three collaborators:

    * **QDecorationRoleProxyModel** — sits between the source model and the
      view, holding the resolved ``DecorationRole`` pixmaps separately from
      the source data so the source model stays free of image state.
    * **QGridIconDelegate** (inherited) — emits ``requestImage`` the first
      time a visible cell has no ``DecorationRole`` data, driving lazy loading.
    * **icon_pixmap_getter** — a callable ``(emoji: str, size: QSize, dpr: float)
      → QPixmap`` responsible for resolving an emoji character to a pixmap.
      Defaults to :meth:`QEmojiImageProvider.getPixmap` when not supplied.

    Lazy-loading flow
    -----------------
    1. The delegate paints a placeholder and emits ``requestImage``.
    2. :meth:`_on_request_image` calls the getter and writes the result into
       the proxy model's ``DecorationRole``.
    3. The model emits ``dataChanged``, the delegate repaints with the real image.
    """

    def __init__(
        self,
        parent: typing.Optional[QWidget] = None,
        icon_pixmap_getter: typing.Optional[typing.Callable[[str, QSize, float], QPixmap]] = None,
    ):
        """
        Initialize the QEmojiView.

        Args:
            parent (Optional[QWidget]): The parent widget. Defaults to None.
            icon_pixmap_getter (Optional[Callable[[str, QSize, float], QPixmap]]): A callable
                with signature ``(emoji: str, size: QSize, dpr: float) -> QPixmap`` used to
                resolve an emoji character to a scaled, HiDPI-aware pixmap.
                If ``None``, a default :class:`QEmojiImageProvider` is created and its
                :meth:`~QEmojiImageProvider.getPixmap` method is used.
        """
        super(QEmojiView, self).__init__(parent)
        self.setModel(QDecorationRoleProxyModel())

        if icon_pixmap_getter is None:
            self._emoji_image_provider = QEmojiImageProvider()
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
            self._emoji_image_provider.fontFamilyChanged.connect(self._on_image_provider_settings_changed)

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
        icon_pixmap_getter: typing.Callable[[str, QSize, float], QPixmap],
    ) -> None:
        """
        Replace the strategy used to resolve emoji characters to pixmaps.

        After storing the new callable, calls :meth:`~QGridIconDelegate.forceReloadAll`
        on the delegate so all previously cached request states are cleared and
        every visible item will trigger a fresh load with the new getter.

        Args:
            icon_pixmap_getter (Callable[[str, QSize, float], QPixmap]): A callable
                with signature ``(emoji: str, size: QSize, dpr: float) -> QPixmap``.
                ``size`` is the logical target size; ``dpr`` is the device pixel ratio
                of the screen the view is currently on.
        """
        self._icon_pixmap_getter = icon_pixmap_getter

        delegate = self.itemDelegate()
        delegate.forceReloadAll()

    def iconPixmapGetter(self) -> typing.Callable[[str, QSize, float], QPixmap]:
        """
        Return the current pixmap getter callable.

        Returns:
            Callable[[str, QSize, float], QPixmap]: The callable currently used to
            resolve emoji characters to pixmaps.  Its signature is
            ``(emoji: str, size: QSize, dpr: float) -> QPixmap``.
        """
        return self._icon_pixmap_getter

    def emojiImageProvider(self) -> typing.Optional[QEmojiImageProvider]:
        """
        Return the internal :class:`QEmojiImageProvider`, if any.

        Returns ``None`` when a custom ``icon_pixmap_getter`` was supplied at
        construction time, since no provider is created in that case.

        Returns:
            Optional[QEmojiImageProvider]: The default provider instance, or
            ``None`` if a custom getter is in use.
        """
        return self._emoji_image_provider

    # -------------------------------------------------------------------------
    # Internal Slots & Callbacks
    # -------------------------------------------------------------------------

    @Slot(QPersistentModelIndex, QSize, float)
    def _on_request_image(self, persistent_index: QPersistentModelIndex, size: QSize, dpr: float) -> None:
        """
        Load and store the emoji pixmap when requested by the delegate.

        Connected to :attr:`~QGridIconDelegate.requestImage`.  Reads the emoji
        character from the item's ``EditRole``, resolves it to a ``QPixmap``
        via the current getter, and writes the result back into the proxy
        model's ``DecorationRole``, which triggers a ``dataChanged`` emission
        and causes the delegate to repaint the cell with the real image.

        Early-returns without side effects when the index is invalid, no getter
        is set, or the item carries no emoji string.

        Args:
            persistent_index (QPersistentModelIndex): Index of the item that
                needs its image loaded.
            size (QSize): Logical target size requested by the delegate for
                the current cell.
            dpr (float): Device pixel ratio of the screen the view is on,
                forwarded to the getter so it can produce a HiDPI-aware pixmap.
        """
        if not persistent_index.isValid():
            return

        icon_pixmap_getter = self.iconPixmapGetter()

        if not icon_pixmap_getter:
            return

        emoji = persistent_index.data(Qt.ItemDataRole.EditRole)

        if emoji is None:
            return

        pixmap = icon_pixmap_getter(emoji, size, dpr)
        proxy = self.model()
        proxy.setData(persistent_index, pixmap, Qt.ItemDataRole.DecorationRole)

    @Slot()
    def _on_image_provider_settings_changed(self) -> None:
        """
        Handle a change in the image provider's rendering source.

        Connected to :attr:`~QEmojiImageProvider.sourceChanged`.  Calls
        :meth:`~QGridIconDelegate.forceReloadAll` on the delegate so that all
        items discard their cached request state and re-emit ``requestImage``
        on the next paint, ensuring the view reflects the new source.
        """
        delegate = self.itemDelegate()
        delegate.forceReloadAll()