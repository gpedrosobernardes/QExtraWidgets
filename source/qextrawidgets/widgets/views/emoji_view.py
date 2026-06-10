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


    def __init__(
        self,
        parent: typing.Optional[QWidget] = None,
    ):
        super(QEmojiView, self).__init__(parent)
        self.setModel(QDecorationRoleProxyModel())

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