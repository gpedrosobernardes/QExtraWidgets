from enum import Enum

from PySide6.QtCore import QT_TRANSLATE_NOOP, Signal
from PySide6.QtGui import QStandardItemModel, Qt
from emoji_data_python import emoji_data

from qextrawidgets.emoji_utils import EmojiImageProvider
from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.items.emoji_category_item import QEmojiCategoryItem
from qextrawidgets.items.emoji_item import QEmojiItem, QEmojiDataRole
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

    def __init__(self, favorite_category: bool = True, recent_category: bool = True):
        super().__init__()
        self._favorite_category = favorite_category
        self._recent_category = recent_category

    def populate(self):
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
                item = QEmojiItem(emoji_char.char, emoji_char.short_names)
                if emoji_char.category not in emoji_grouped_by_category:
                    emoji_grouped_by_category[emoji_char.category] = []
                emoji_grouped_by_category[emoji_char.category].append(item)

        for category, emoji_items in emoji_grouped_by_category.items():
            icon = QThemeResponsiveIcon.fromAwesome(icons[category])
            category_item = QEmojiCategoryItem(category, icon)
            self.appendRow(category_item)
            category_item.appendRows(emoji_items)
            self.categoryInserted.emit(category_item)

        if self._favorite_category:
            icon = QThemeResponsiveIcon.fromAwesome(icons[EmojiCategory.Favorites])
            favorite_category_item = QEmojiCategoryItem(EmojiCategory.Favorites, icon)
            self.appendRow(favorite_category_item)
            self.categoryInserted.emit(favorite_category_item)

        if self._recent_category:
            icon = QThemeResponsiveIcon.fromAwesome(icons[EmojiCategory.Recents])
            recent_category_item = QEmojiCategoryItem(EmojiCategory.Recents, icon)
            self.appendRow(recent_category_item)
            self.categoryInserted.emit(recent_category_item)

    def setExpanded(self, value: bool):
        for row in range(self.rowCount()):
            self.setData(self.index(row, 0), value, role=QGroupedIconView.ExpansionStateRole)

    def findEmojiInCategory(self, category_index, emoji):
        # match(start_index, role, value, hits, flags)
        # Procuramos a partir do primeiro filho da categoria
        start_index = self.index(0, 0, category_index)

        # Qt.MatchRecursive permite buscar em toda a profundidade,
        # mas aqui queremos apenas nos filhos diretos, então não usamos essa flag se não precisarmos.
        matches = self.match(
            start_index,
            Qt.ItemDataRole.EditRole,  # Ou Qt.ItemDataRole.EditRole para o emoji
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