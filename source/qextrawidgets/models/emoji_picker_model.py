import typing
from enum import Enum

from PySide6.QtCore import QT_TRANSLATE_NOOP, Signal, QModelIndex
from PySide6.QtGui import QStandardItemModel, Qt
from emoji_data_python import emoji_data, EmojiChar

from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.items.emoji_category_item import QEmojiCategoryItem
from qextrawidgets.items.emoji_item import QEmojiItem, QEmojiDataRole, EmojiSkinTone
from qextrawidgets.views.grouped_icon_view import QGroupedIconView


class EmojiCategory(str, Enum):
    """Standard emoji categories."""
    Activities = QT_TRANSLATE_NOOP("EmojiCategory", "Activities")
    FoodAndDrink = QT_TRANSLATE_NOOP("EmojiCategory", "Food & Drink")
    AnimalsAndNature = QT_TRANSLATE_NOOP("EmojiCategory", "Animals & Nature")
    PeopleAndBody = QT_TRANSLATE_NOOP("EmojiCategory", "People & Body")
    Symbols = QT_TRANSLATE_NOOP("EmojiCategory", "Symbols")
    Flags = QT_TRANSLATE_NOOP("EmojiCategory", "Flags")
    TravelAndPlaces = QT_TRANSLATE_NOOP("EmojiCategory", "Travel & Places")
    Objects = QT_TRANSLATE_NOOP("EmojiCategory", "Objects")
    SmileysAndEmotion = QT_TRANSLATE_NOOP("EmojiCategory", "Smileys & Emotion")
    Favorites = QT_TRANSLATE_NOOP("EmojiCategory", "Favorites")
    Recents = QT_TRANSLATE_NOOP("EmojiCategory", "Recents")


class QEmojiPickerModel(QStandardItemModel):
    categoryInserted = Signal(QEmojiCategoryItem)
    skinToneChanged = Signal(QModelIndex)
    _emojis_skin_modifier_compatible = {}

    def __init__(self, favorite_category: bool = True, recent_category: bool = True):
        super().__init__()
        self._favorite_category = favorite_category
        self._recent_category = recent_category

    def populate(self):
        self._emojis_skin_modifier_compatible.clear()

        icons = {
            EmojiCategory.Activities: "fa6s.gamepad",
            EmojiCategory.FoodAndDrink: "fa6s.bowl-food",
            EmojiCategory.AnimalsAndNature: "fa6s.leaf",
            EmojiCategory.PeopleAndBody: "fa6s.user",
            EmojiCategory.Symbols: "fa6s.heart",
            EmojiCategory.Flags: "fa6s.flag",
            EmojiCategory.TravelAndPlaces: "fa6s.bicycle",
            EmojiCategory.Objects: "fa6s.lightbulb",
            EmojiCategory.SmileysAndEmotion: "fa6s.face-smile",
            EmojiCategory.Favorites: "fa6s.star",
            EmojiCategory.Recents: "fa6s.clock-rotate-left"
        }

        emoji_grouped_by_category = {}

        for emoji_char in sorted(emoji_data, key=lambda e: e.sort_order):
            if emoji_char.category != "Component":
                item = QEmojiItem(emoji_char)
                if emoji_char.category not in emoji_grouped_by_category:
                    emoji_grouped_by_category[emoji_char.category] = []
                emoji_grouped_by_category[emoji_char.category].append(item)
                support_skin_modifiers = QEmojiItem.skinToneCompatible(emoji_char)
                if support_skin_modifiers:
                    if emoji_char.category not in self._emojis_skin_modifier_compatible:
                        self._emojis_skin_modifier_compatible[emoji_char.category] = []
                    self._emojis_skin_modifier_compatible[emoji_char.category].append(emoji_char.char)

        if self._recent_category:
            icon = QThemeResponsiveIcon.fromAwesome(icons[EmojiCategory.Recents])
            recent_category_item = QEmojiCategoryItem(EmojiCategory.Recents, icon)
            self.appendRow(recent_category_item)
            self.categoryInserted.emit(recent_category_item)

        if self._favorite_category:
            icon = QThemeResponsiveIcon.fromAwesome(icons[EmojiCategory.Favorites])
            favorite_category_item = QEmojiCategoryItem(EmojiCategory.Favorites, icon)
            self.appendRow(favorite_category_item)
            self.categoryInserted.emit(favorite_category_item)

        for category, emoji_items in emoji_grouped_by_category.items():
            icon = QThemeResponsiveIcon.fromAwesome(icons[category])
            category_item = QEmojiCategoryItem(category, icon)
            self.appendRow(category_item)
            category_item.appendRows(emoji_items)
            self.categoryInserted.emit(category_item)

    def setExpanded(self, value: bool):
        for row in range(self.rowCount()):
            self.setData(self.index(row, 0), value, role=QEmojiCategoryItem.ExpansionStateRole)

    def findEmojiInCategory(self, category_index, emoji):
        # match(start_index, role, value, hits, flags)
        # Procuramos a partir do primeiro filho da categoria
        start_index = self.index(0, 0, category_index)

        # Qt.MatchRecursive permite buscar em toda a profundidade,
        # mas aqui queremos apenas nos filhos diretos, então não usamos essa flag se não precisarmos.
        matches = self.match(
            start_index,
            QEmojiDataRole.EmojiRole,  # Ou Qt.ItemDataRole.EditRole para o emoji
            emoji,
            1,  # Número de resultados (1 para parar no primeiro)
            Qt.MatchFlag.MatchExactly
        )

        if matches:
            return matches[0]  # Retorna o QModelIndex encontrado
        return None

    def findCategory(self, category: str):
        start_index = self.index(0, 0)
        matches = self.match(
            start_index,
            QEmojiDataRole.CategoryRole,
            category,
            1,
            Qt.MatchFlag.MatchExactly)
        if matches:
            return matches[0]
        return None

    def setSkinTone(self, skin_tone: str):
        for category, emojis_with_skin_modifier in self._emojis_skin_modifier_compatible.items():
            category_index = self.findCategory(category)
            if not category_index:
                return

            for emoji in emojis_with_skin_modifier:
                emoji_index = self.findEmojiInCategory(category_index, emoji)
                if not emoji_index:
                    continue

                emoji_item = self.itemFromIndex(emoji_index)
                emoji_item.setData(skin_tone, QEmojiDataRole.SkinToneRole)
                self.skinToneChanged.emit(emoji_index)
