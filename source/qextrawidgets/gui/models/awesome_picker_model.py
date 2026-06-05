import typing

import qtawesome
from PySide6.QtGui import QStandardItem

from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.gui.items import QIconCategoryItem
from qextrawidgets.gui.items.awesome_item import QAwesomeItem
from qextrawidgets.gui.models import QIconPickerModel


class QAwesomePickerModel(QIconPickerModel):
    def __init__(self,
                 parent=None,
                 recent_category: bool = True,
                 favorite_category: bool = True,
                 ignored_categories: typing.Optional[typing.List[str]] = None):
        super(QAwesomePickerModel, self).__init__(parent, recent_category, favorite_category, ignored_categories)

    def populate(self,
                 recent_category: bool = True,
                 favorite_category: bool = True,
                 ignored_categories: typing.Optional[typing.List[str]] = None):
        super(QAwesomePickerModel, self).populate(
            recent_category=recent_category,
            favorite_category=favorite_category,
        )
        qtawesome._instance()
        font_maps = qtawesome._resource["iconic"].charmap
        font_names = qtawesome._resource["iconic"].fontname

        icons = {
            "fa5": "fa5.font-awesome-logo-full",
            "fa5s": "fa5s.font-awesome-logo-full",
            "fa5b": "fa5b.font-awesome-flag",
            "fa6": "fa6.font-awesome",
            "fa6s": "fa6s.font-awesome",
            "fa6b": "fa6b.font-awesome",
            "mdi": "mdi.material-design",
            "mdi6": "mdi6.material-design",
            "ei": "ei.redux",
            "ph": "ph.phosphor-logo",
            "ri": "ri.remixicon-fill",
            "msc": "mdi.microsoft-visual-studio"
        }

        if ignored_categories is None:
            ignored_categories = []

        for font_collection, font_data in font_maps.items():
            if font_collection not in ignored_categories:
                font_name = font_names[font_collection]
                category = QIconCategoryItem(font_name, font_collection, QThemeResponsiveIcon.fromAwesome(icons[font_collection]))
                self.appendRow(category)

                for icon_name in font_data:
                    item = QAwesomeItem(f"{font_collection}.{icon_name}")
                    category.appendRow(item)
