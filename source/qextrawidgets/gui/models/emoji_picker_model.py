import logging
import time
import typing
from enum import Enum

from PySide6.QtCore import QT_TRANSLATE_NOOP
from PySide6.QtGui import Qt
from emoji_data_python import emoji_data

from qextrawidgets.core.utils.emojis import EmojiSkinVariations, QEmojiUtils
from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.gui.items.emoji_item import QEmojiItem
from qextrawidgets.gui.models import QIconPickerModel


class QEmojiPickerModel(QIconPickerModel):

    class EmojiCategory(str, Enum):
        """Standard emoji categories."""
        SmileysAndEmotion = QT_TRANSLATE_NOOP("EmojiCategory", "Smileys & Emotion")
        PeopleAndBody = QT_TRANSLATE_NOOP("EmojiCategory", "People & Body")
        AnimalsAndNature = QT_TRANSLATE_NOOP("EmojiCategory", "Animals & Nature")
        FoodAndDrink = QT_TRANSLATE_NOOP("EmojiCategory", "Food & Drink")
        Symbols = QT_TRANSLATE_NOOP("EmojiCategory", "Symbols")
        Activities = QT_TRANSLATE_NOOP("EmojiCategory", "Activities")
        Objects = QT_TRANSLATE_NOOP("EmojiCategory", "Objects")
        TravelAndPlaces = QT_TRANSLATE_NOOP("EmojiCategory", "Travel & Places")
        Flags = QT_TRANSLATE_NOOP("EmojiCategory", "Flags")

    def __init__(self,
                 parent=None,
                 recent_category: bool = True,
                 favorite_category: bool = True,
                 ignored_categories: typing.Optional[typing.List[str]] = None):
        super(QEmojiPickerModel, self).__init__(parent, recent_category, favorite_category, ignored_categories)

    def populate(self,
                 recent_category: bool = True,
                 favorite_category: bool = True,
                 ignored_categories: typing.Optional[typing.List[str]] = None):
        super(QEmojiPickerModel, self).populate(
            recent_category=recent_category,
            favorite_category=favorite_category,
        )

        if ignored_categories is None:
            ignored_categories = []

        icons = {
            QEmojiPickerModel.EmojiCategory.SmileysAndEmotion: "fa6s.face-smile",
            QEmojiPickerModel.EmojiCategory.PeopleAndBody: "fa6s.user",
            QEmojiPickerModel.EmojiCategory.AnimalsAndNature: "fa6s.leaf",
            QEmojiPickerModel.EmojiCategory.FoodAndDrink: "fa6s.bowl-food",
            QEmojiPickerModel.EmojiCategory.Activities: "fa6s.gamepad",
            QEmojiPickerModel.EmojiCategory.TravelAndPlaces: "fa6s.bicycle",
            QEmojiPickerModel.EmojiCategory.Objects: "fa6s.lightbulb",
            QEmojiPickerModel.EmojiCategory.Symbols: "fa6s.heart",
            QEmojiPickerModel.EmojiCategory.Flags: "fa6s.flag",
        }

        start = time.perf_counter()

        for category in icons.keys():
            if category not in ignored_categories:
                icon = QThemeResponsiveIcon.fromAwesome(
                    icons[category], options=[{"scale_factor": 0.9}]
                )
                category_item = self.addCategory(category, category, icon)

                try:
                    emoji_chars = QEmojiUtils.getEmojiCharsByCategory(category)
                except KeyError:
                    continue
                else:
                    for emoji_char in sorted(emoji_chars, key=lambda e: e.sort_order):
                        category_item.appendRow(QEmojiItem(emoji_char))

        end = time.perf_counter()
        logging.debug(f"Populated emoji model in {end - start:.6f} seconds.")

    def setSkinVariation(self, skin_variation: typing.Optional[EmojiSkinVariations]) -> None:
        start = time.perf_counter()

        for row in range(self.rowCount()):
            category_item = self.item(row)

            for child_row in range(category_item.rowCount()):
                item = category_item.child(child_row)

                emoji_char = item.data(Qt.ItemDataRole.EditRole)
                skin_varied_emoji_char = QEmojiUtils.applySkinVariation(emoji_char, skin_variation)
                if emoji_char != skin_varied_emoji_char:
                    item.setData(skin_varied_emoji_char, Qt.ItemDataRole.EditRole)
                    self.requestIcon.emit(item.index())
                    logging.debug("Defined ColorModifierRole for {}".format(emoji_char.char))

        end = time.perf_counter()
        logging.debug(f"Finished setColorModifier in {end - start:.6f} seconds.")