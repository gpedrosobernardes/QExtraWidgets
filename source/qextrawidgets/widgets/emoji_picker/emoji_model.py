import typing

from PySide6.QtCore import QSize, QModelIndex, Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt, QIcon
from PySide6.QtWidgets import QWidget
from emoji_data_python import EmojiChar, emoji_data

from qextrawidgets.widgets.emoji_picker.emoji_item import QEmojiItem
from qextrawidgets.widgets.emoji_picker.emoji_sort_filter import QEmojiSortFilterProxyModel
from qextrawidgets.widgets.emoji_picker.enums import QEmojiDataRole, EmojiSkinTone


class QEmojiModel(QStandardItemModel):
    """A standard item model specialized for storing and managing emoji data.

    Signals:
        favoriteChanged (str, bool): Emitted when an emoji's favorite status changes.
        recentChanged (str, bool): Emitted when an emoji's recent status changes.
    """

    favoriteChanged = Signal(str, bool)
    recentChanged = Signal(str, bool)

    def __init__(self, parent: QWidget = None) -> None:
        """Initializes the emoji model.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._emoji_size_hint = None

    def itemFromProxyIndex(self, proxy_index: QModelIndex) -> typing.Optional[QEmojiItem]:
        """Returns the source model item corresponding to the given proxy index.

        Args:
            proxy_index (QModelIndex): The index from the proxy model.

        Returns:
            QStandardItem, optional: The corresponding item in the source model, or None.
        """
        proxy: QEmojiSortFilterProxyModel = proxy_index.model()
        model_index = proxy.mapToSource(proxy_index)
        return self.itemFromIndex(model_index)

    def addEmoji(self, emoji: str, alias: str, category: str, recent: bool = False, favorite: bool = False,
                 skin_tones: typing.Dict[EmojiSkinTone, str] = None) -> None:
        """Adds a new emoji to the model with its metadata.

        Args:
            emoji (str): The emoji character (usually unicode).
            alias (str): The text alias (e.g., ":smile:").
            category (str): The category the emoji belongs to.
            recent (bool, optional): Whether the emoji is in the recent list. Defaults to False.
            favorite (bool, optional): Whether the emoji is a favorite. Defaults to False.
            skin_tones (Dict[EmojiSkinTone, str], optional): Dictionary mapping skin tones to emoji variations. Defaults to None.
        """
        item = QEmojiItem(emoji, alias, category, recent, favorite, skin_tones)
        self.appendRow(item)

    def setSkinTone(self, skin_tone: str) -> None:
        """Updates the displayed emoji for all items that support skin tones.

        Args:
            skin_tone (str): The skin tone modifier key.
        """
        for row in range(self.rowCount()):
            item = self.item(row)
            skin_tones: dict = item.data(QEmojiDataRole.SkinTonesRole)
            if skin_tones:
                item.setData(skin_tones[skin_tone], Qt.ItemDataRole.EditRole)

    def emojiItem(self, emoji: str) -> typing.Optional[QEmojiItem]:
        """Finds and returns the item for a specific emoji character.

        Args:
            emoji (str): The emoji character to search for.

        Returns:
            QStandardItem, optional: The found item, or None.
        """
        items = self.findItems(emoji, Qt.MatchFlag.MatchExactly, column=0)
        if items:
            return items[0]
        return None

    def filterEmojisItems(self, role: typing.Union[QEmojiDataRole, Qt.ItemDataRole], value: typing.Any) -> typing.List[QStandardItem]:
        """Filters model items based on a specific role and value.

        Args:
            role (Union[QEmojiDataRole, ItemDataRole]): The role to filter by.
            value (Any): The value to match.

        Returns:
            List[QStandardItem]: A list of items that match the criteria.
        """
        return [self.itemFromIndex(index) for index in self.match(self.index(0, 0), role, value, -1, Qt.MatchFlag.MatchExactly)]

    def getEmojiItems(self) -> typing.List[QStandardItem]:
        """Returns a list of all emoji items in the model.

        Returns:
            List[QStandardItem]: List of all items.
        """
        return [self.item(row) for row in range(self.rowCount())]

    def removeEmoji(self, emoji: typing.Union[QEmojiItem, str]) -> None:
        """Removes an emoji from the model.

        Args:
            emoji (str): The emoji character to remove.
        """
        if isinstance(emoji, QEmojiItem):
            item = emoji
        else:
            item = self.emojiItem(emoji)
        if item:
            self.removeRow(item.row())

    def setFavoriteEmoji(self, emoji: typing.Union[QEmojiItem, str], favorite: bool) -> None:
        """Sets the favorite status of an emoji.

        Args:
            emoji (str): The emoji character.
            favorite (bool): The new favorite status.
        """
        if isinstance(emoji, QEmojiItem):
            item = emoji
        else:
            item = self.emojiItem(emoji)
        if item:
            item.setData(favorite, QEmojiDataRole.FavoriteRole)
            self.favoriteChanged.emit(item.emoji(), favorite)

    def setRecentEmoji(self, emoji: typing.Union[QEmojiItem, str], recent: bool) -> None:
        """Sets the recent status of an emoji.

        Args:
            emoji (str): The emoji character.
            recent (bool): The new recent status.
        """
        if isinstance(emoji, QEmojiItem):
            item = emoji
        else:
            item = self.emojiItem(emoji)
        if item:
            item.setData(recent, QEmojiDataRole.RecentRole)
            self.recentChanged.emit(item.emoji(), recent)

    def clearEmojis(self) -> None:
        """Clears icons and text for all emoji items in the model."""
        for row in range(self.rowCount()):
            item = self.item(row)
            item.setIcon(QIcon())
            item.setText("")

    def populate(self) -> None:
        """Populates the picker with standard emoji categories."""
        self.beginResetModel()
        for data in sorted(emoji_data, key=lambda emoji_: emoji_.sort_order):
            if data.has_img_twitter and data.category != "Component":
                skin_tones = self._get_emoji_skin_tones_dict(data.char, data.skin_variations)
                alias = " ".join(f":{alias}:" for alias in data.short_names)
                self.addEmoji(data.char, alias, data.category, skin_tones=skin_tones)
        self.endResetModel()

    @staticmethod
    def _get_emoji_skin_tones_dict(emoji: str, skin_variations: typing.Dict[str, EmojiChar]) -> typing.Optional[typing.Dict[EmojiSkinTone, str]]:
        """Maps skin tone modifiers to actual emoji strings.

        Args:
            emoji (str): Base emoji string.
            skin_variations (Dict[str, EmojiChar]): Available skin variations.

        Returns:
            Dict[EmojiSkinTone, str], optional: Dictionary mapping skin tones to emoji strings or None.
        """
        if skin_variations:
            skin_tones = {skin_tone: found_skin_tone.char for skin_tone in list(EmojiSkinTone) if
                          (found_skin_tone := skin_variations.get(skin_tone))}
            if skin_tones:
                skin_tones[EmojiSkinTone.Default] = emoji
            return skin_tones
        return None