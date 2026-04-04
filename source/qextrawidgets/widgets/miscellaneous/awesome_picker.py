import random
import typing

import qtawesome
from PySide6.QtGui import QPixmap, Qt

from qextrawidgets.gui.items.icon_item import QIconItem
from qextrawidgets.gui.models.icon_picker_model import QIconPickerModel
from qextrawidgets.widgets.miscellaneous.icon_picker import QIconPicker


class QAwesomePicker(QIconPicker):
    def __init__(self, parent = None, model: typing.Optional[QIconPickerModel] = None, icon_label_size: int = 32):
        """
        Initialize the QAwesomePicker class.
        Fill the color selector with a bunch of color options of a random icon.

        Args:
            parent (QWidget, optional): The parent widget.
            model (QIconPickerModel, optional): The QIconPickerModel instance. Uses a populated QIconPickerModel with QtAwesome icons if None.
            icon_label_size (int, optional): The size of the icon label. Defaults to 32.
        """
        if model is None:
            model = QIconPickerModel(QIconPickerModel.PopulateSource.AwesomeIcons)

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
            "#FF007F"  # Rosa-Choque
        ]

        for color in colors:
            icon_item = QIconItem(random_icon, True, color_modifier=color)
            self.addColorOption(icon_item)

    def iconPixmapGetter(self) -> typing.Callable[[QIconItem], QPixmap]:
        """Define the icon getter that returns the icon pixmap from QtAwesome."""
        view = self.view()
        def getter(item: QIconItem) -> QPixmap:
            name = item.data(Qt.ItemDataRole.EditRole)
            color = item.data(QIconItem.QIconItemDataRole.ColorModifierRole)
            if color:
                icon = qtawesome.icon(name, color=color)
            else:
                icon = qtawesome.icon(name)
            return icon.pixmap(view.iconSize())
        return getter
