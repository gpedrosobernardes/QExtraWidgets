import random
import typing

import qtawesome
from PySide6.QtCore import QSize, Slot
from PySide6.QtGui import QPixmap, Qt, QStandardItem

from qextrawidgets.gui.models.awesome_picker_model import QAwesomePickerModel
from qextrawidgets.widgets.miscellaneous.icon_picker import QIconPicker


class QAwesomePicker(QIconPicker):
    def __init__(self, parent = None, model: typing.Optional[QAwesomePickerModel] = None, icon_label_size: int = 32):
        """
        Initialize the QAwesomePicker class.
        Fill the color selector with a bunch of color options of a random icon.

        Args:
            parent (QWidget, optional): The parent widget.
            model (QIconPickerModel, optional): The QIconPickerModel instance. Uses a populated QIconPickerModel with QtAwesome icons if None.
            icon_label_size (int, optional): The size of the icon label. Defaults to 32.
        """
        if model is None:
            model = QAwesomePickerModel()

        super().__init__(parent, model, icon_label_size)

        qtawesome._instance()
        font_maps = qtawesome._resource["iconic"].charmap
        icons = [f"{font_collection}.{font_name}" for font_collection, font_data in font_maps.items() for font_name in font_data if "grin" in font_name]
        random_icon = random.choice(icons)

        colors = [
            # Neutros (Fundamentais)
            "#FFFFFF",  # Branco
            "#808080",  # Cinza Médio
            "#000000",  # Preto

            # Círculo Cromático (12 Cores)
            "#FF0000",  # Vermelho
            "#FF7F00",  # Laranja
            "#FFFF00",  # Amarelo
            "#7FFF00",  # Lima
            "#00FF00",  # Verde
            "#00FF7F",  # Verde-Ciano
            "#00FFFF",  # Ciano
            "#007FFF",  # Azul Celeste
            "#0000FF",  # Azul
            "#7F00FF",  # Violeta
            "#FF00FF",  # Magenta
            "#FF007F"   # Rosa-Choque
        ]

        for color in colors:
            icon_item = QStandardItem()
            icon_item.setData(random_icon, Qt.ItemDataRole.EditRole)
            icon_item.setData(qtawesome.icon(random_icon, color=color), Qt.ItemDataRole.DecorationRole)
            icon_item.setData(color, Qt.ItemDataRole.UserRole)
            self.addColorOption(icon_item)

    def iconPixmapGetter(self) -> typing.Callable[[QStandardItem, QSize, float], QPixmap]:
        """Define the icon getter that returns the icon pixmap from QtAwesome."""

        def getter(item: QStandardItem, size: QSize, dpr: float) -> QPixmap:
            name = item.data(Qt.ItemDataRole.EditRole)

            item = self._color_modifier_selector.currentData()
            color = item.data(Qt.ItemDataRole.UserRole)

            if color:
                icon = qtawesome.icon(name, color=color)
            else:
                icon = qtawesome.icon(name)

            physical_size = size * dpr
            pixmap = icon.pixmap(physical_size)
            pixmap.setDevicePixelRatio(dpr)
            return pixmap

        return getter

    @Slot(QStandardItem)
    def _on_set_color_modifier(self, icon_item: QStandardItem) -> None:
        """Updates the skin tone of the emojis.

        Args:
            icon_item (QIconItem): QIconItem instance representing the color_modifier.
        """
        delegate = self.delegate()
        delegate.forceReloadAll()