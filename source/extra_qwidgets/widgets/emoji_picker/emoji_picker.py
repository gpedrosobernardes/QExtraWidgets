import typing

import qtawesome
from PySide6.QtCore import QCoreApplication, Signal, QSize
from PySide6.QtGui import QAction, QStandardItem, QFont
from PySide6.QtWidgets import (QLineEdit, QHBoxLayout, QLabel, QVBoxLayout,
                               QMenu, QWidget, QApplication, QButtonGroup)
# Mocks para as libs externas mencionadas no seu código original
# from extra_qwidgets.widgets.accordion import QAccordion
from emojis.db import Emoji, get_emojis_by_category, get_categories

from extra_qwidgets.icons import QThemeResponsiveIcon
from extra_qwidgets.widgets.accordion import QAccordion
from extra_qwidgets.widgets.accordion_item import QAccordionItem
from extra_qwidgets.widgets.emoji_picker.emoji_category import EmojiCategory
from extra_qwidgets.widgets.emoji_picker.emoji_grid import QEmojiGrid
from extra_qwidgets.widgets.emoji_picker.emoji_image_provider import EmojiImageProvider


class QEmojiPicker(QWidget):
    # Sinais
    picked = Signal(Emoji)  # Emoji object
    favorite = Signal(Emoji, QStandardItem)
    removedFavorite = Signal(Emoji, QStandardItem)  # renomeado para camelCase

    _translations = {
        "Activities": QCoreApplication.translate("QEmojiPicker", "Activities"),
        "Food & Drink": QCoreApplication.translate("QEmojiPicker", "Food & Drink"),
        "Animals & Nature": QCoreApplication.translate("QEmojiPicker", "Animals & Nature"),
        "People & Body": QCoreApplication.translate("QEmojiPicker", "People & Body"),
        "Symbols": QCoreApplication.translate("QEmojiPicker", "Symbols"),
        "Flags": QCoreApplication.translate("QEmojiPicker", "Flags"),
        "Travel & Places": QCoreApplication.translate("QEmojiPicker", "Travel & Places"),
        "Objects": QCoreApplication.translate("QEmojiPicker", "Objects"),
        "Smileys & Emotion": QCoreApplication.translate("QEmojiPicker", "Smileys & Emotion"),
        "Favorites": QCoreApplication.translate("QEmojiPicker", "Favorites"),
        "Recent": QCoreApplication.translate("QEmojiPicker", "Recent")
    }

    def __init__(self, favorite_category: bool = True, recent_category: bool = True):
        super().__init__()

        self._icons = {
            "Activities": QThemeResponsiveIcon.fromAwesome("fa6s.gamepad", options=[{"scale_factor": 0.9}]),
            "Food & Drink": QThemeResponsiveIcon.fromAwesome("fa6s.bowl-food"),
            "Animals & Nature": QThemeResponsiveIcon.fromAwesome("fa6s.leaf"),
            "People & Body": QThemeResponsiveIcon.fromAwesome("fa6s.user"),
            "Symbols": QThemeResponsiveIcon.fromAwesome("fa6s.heart"),
            "Flags": QThemeResponsiveIcon.fromAwesome("fa6s.flag"),
            "Travel & Places": QThemeResponsiveIcon.fromAwesome("fa6s.bicycle", options=[{"scale_factor": 0.9}]),
            "Objects": QThemeResponsiveIcon.fromAwesome("fa6s.lightbulb"),
            "Smileys & Emotion": QThemeResponsiveIcon.fromAwesome("fa6s.face-smile"),
            "Favorites": QThemeResponsiveIcon.fromAwesome("fa6s.star"),
            "Recent": QThemeResponsiveIcon.fromAwesome("fa6s.clock-rotate-left")
        }

        # Variáveis privadas
        self.__favorite_category = None
        self.__recent_category = None
        self.__categories_data = {}  # Guarda referencias dos grids e layouts
        # Layout dentro do scroll area onde os grids ficam
        self.__accordion = QAccordion()

        # Layout principal
        self.__main_layout = QVBoxLayout(self)
        self.__main_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Barra de Busca
        self.__line_edit = self._create_search_line_edit()

        self.__main_layout.addWidget(self.__line_edit)

        self._shortcuts_container = QWidget()
        self._shortcuts_container.setFixedHeight(40)  # Altura fixa para a barra
        self._shortcuts_layout = QHBoxLayout(self._shortcuts_container)
        self._shortcuts_layout.setContentsMargins(5, 0, 5, 0)
        self._shortcuts_layout.setSpacing(2)

        self._shortcuts_group = QButtonGroup(self)
        self._shortcuts_group.setExclusive(True)
        self.__main_layout.addWidget(self._shortcuts_container)

        self.__emoji_label = QLabel()
        self.__emoji_label.setFixedSize(QSize(32, 32))
        self.__emoji_label.setScaledContents(True)
        self.__aliases_emoji_label = self._create_emoji_label()
        self._accordion = QAccordion()
        self.__menu_horizontal_layout = QHBoxLayout()
        self.__content_layout = QHBoxLayout()
        self.__content_layout.addWidget(self.__emoji_label)
        self.__content_layout.addWidget(self.__aliases_emoji_label, True)

        self.__main_layout.addWidget(self.__accordion)
        self.__main_layout.addLayout(self.__content_layout)

        self.__setup_connections()

        # Popula categorias (Idealmente isso seria Lazy, chamado apenas quando necessário)
        self.__add_base_categories()

        self.setFavoriteCategory(favorite_category)
        self.setRecentCategory(recent_category)

        self.__accordion.expandAll()

    def __setup_connections(self):
        self.__line_edit.textChanged.connect(self.__filter_emojis)
        self.__accordion.enteredSection.connect(self.__on_entered_section)
        self.__accordion.leftSection.connect(self.__on_left_section)

    def __on_entered_section(self, section: QAccordionItem):
        category: EmojiCategory = self.__categories_data[section.objectName()]
        if section.header().isExpanded():
            category.shortcut().setChecked(True)

    def __on_left_section(self, section: QAccordionItem):
        category: EmojiCategory = self.__categories_data[section.objectName()]
        category.shortcut().setChecked(False)

    def __add_base_categories(self):
        """
        Cria as categorias.
        Nota: Em produção, carregue os itens dentro dos grids de forma assíncrona ou lazy.
        """
        # Exemplo de categorias estáticas (substitua pela sua chamada ao DB)
        for category_name in sorted(get_categories()):
            category = EmojiCategory(category_name, self._translations[category_name], self._icons[category_name])
            self.addCategory(category)
            self.__populate_grid_items(category.grid(), category_name)

    def _on_schortcut_clicked(self, section: QAccordionItem):
        self.__accordion.collapseAll()
        section.setExpanded(True)
        QApplication.processEvents()
        self.__accordion.scrollToItem(section)

    @staticmethod
    def __populate_grid_items(grid: QEmojiGrid, category: str):
        """Cria os itens do grid."""
        # Aqui você chamaria get_emojis_by_category(category)
        # Exemplo Mock:
        emojis_mock = get_emojis_by_category(category)

        for emoji in emojis_mock:
            grid.addEmoji(emoji, update_geometry=False)
        grid.updateGeometry()

    def __filter_emojis(self, text: str):
        """Filtra todas as grids."""
        for category in self.__categories_data.values():
            grid = category.grid()
            section = category.accordionItem()

            grid.filterContent(text) # Chama o método de filtro do grid

            # Se o grid ficar vazio após filtro, esconde o título também
            is_empty = grid.allFiltered()
            grid.setVisible(not is_empty)
            section.setVisible(not is_empty)

    def __open_context_menu(self, emoji, item, global_pos):
        menu = QMenu(self)

        # Lógica de Favorito
        if self.__favorite_category:
            favorite_category = self.category("Favorites")
            grid = favorite_category.grid()
            if grid.emojiItem(emoji):
                action_unfav = QAction(QCoreApplication.translate("QEmojiPicker", "Remover dos favoritos"), self)
                action_unfav.triggered.connect(lambda: self.removedFavorite.emit(emoji, item))
                menu.addAction(action_unfav)
            else:
                action_fav = QAction(QCoreApplication.translate("QEmojiPicker", "Adicionar aos favoritos"), self)
                action_fav.triggered.connect(lambda: self.favorite.emit(emoji, item))
                menu.addAction(action_fav)
        copy_alias = QAction(QCoreApplication.translate("QEmojiPicker", "Copiar alias"), self)
        copy_alias.triggered.connect(lambda: self.__copy_emoji_alias(emoji))
        menu.addAction(copy_alias)

        menu.exec(global_pos)

    @staticmethod
    def __copy_emoji_alias(emoji: Emoji):
        clipboard = QApplication.clipboard()
        alias = emoji[0][0]
        clipboard.setText(f":{alias}:")

    def __on_mouse_enter_emoji(self, emoji: Emoji, item):
        pixmap = EmojiImageProvider.get_pixmap(
            emoji,
            self.__emoji_label.size(),
            self.devicePixelRatio()
        )
        self.__emoji_label.setPixmap(pixmap)
        aliases = " ".join(f":{alias}:" for alias in emoji[0])
        self.__aliases_emoji_label.setText(aliases)

    def __on_mouse_left_emoji(self, emoji, item):
        self.__emoji_label.clear()
        self.__aliases_emoji_label.setText("")

    def __on_favorite(self, emoji: Emoji, _: QStandardItem):
        favorite_category = self.category("Favorites")
        grid = favorite_category.grid()
        grid.addEmoji(emoji)

    def __on_unfavorite(self, emoji: Emoji, _: QStandardItem):
        favorite_category = self.category("Favorites")
        grid = favorite_category.grid()
        grid.removeEmoji(emoji)

    def __add_recent(self, emoji: Emoji):
        recent_category = self.category("Recent")
        grid = recent_category.grid()
        if not grid.emojiItem(emoji):
            grid.addEmoji(emoji)

    @staticmethod
    def _create_emoji_label() -> QLabel:
        font = QFont()
        font.setBold(True)
        font.setPointSize(13)
        label = QLabel()
        label.setFont(font)
        return label

    @staticmethod
    def _create_search_line_edit() -> QLineEdit:
        font = QFont()
        font.setPointSize(12)
        line_edit = QLineEdit()
        line_edit.setFont(font)
        line_edit.setPlaceholderText(
            QCoreApplication.translate("QEmojiPicker", "Pesquisar emoji...")
        )
        line_edit.setClearButtonEnabled(True)
        # Ícone de busca usando qtawesome
        line_edit.addAction(QThemeResponsiveIcon.fromAwesome("fa6s.magnifying-glass"), QLineEdit.ActionPosition.LeadingPosition)
        return line_edit

    # --- API Pública (camelCase) ---

    def resetPicker(self):
        """Reseta o estado do picker."""
        self.__line_edit.clear()
        # Scroll para o topo
        self._accordion.scroll.verticalScrollBar().setValue(0)

    def addCategory(self, category: EmojiCategory, shortcut_position: int = -1, section_position: int = -1):
        self.__categories_data[category.name()] = category

        # Grid
        grid = category.grid()
        # Conecta sinais do grid aos sinais do Picker
        grid.emojiClicked.connect(lambda emoji, item: self.picked.emit(emoji))
        grid.mouseEnteredEmoji.connect(self.__on_mouse_enter_emoji)
        grid.mouseLeftEmoji.connect(self.__on_mouse_left_emoji)
        grid.contextMenu.connect(self.__open_context_menu)

        # Seção da Categoria
        section = category.accordionItem()
        self.__accordion.addAccordionItem(section, section_position)

        shortcut = category.shortcut()
        self._shortcuts_layout.insertWidget(shortcut_position, shortcut)
        self._shortcuts_group.addButton(shortcut)

        shortcut.clicked.connect(lambda: self._on_schortcut_clicked(section))

    def removeCategory(self, category: EmojiCategory):
        self.__categories_data.pop(category.name(), None)
        self.__accordion.removeAccordionItem(category.accordionItem())
        self._shortcuts_layout.removeWidget(category.shortcut())
        self._shortcuts_group.removeButton(category.shortcut())
        category.deleteLater()

    def categories(self) -> list[EmojiCategory]:
        return list(self.__categories_data.values())

    def category(self, name: str) -> typing.Optional[EmojiCategory]:
        return self.__categories_data.get(name)

    def setFavoriteCategory(self, active: bool):
        favorite_category = self.category("Favorites")
        if favorite_category and not active:
            self.removeCategory(favorite_category)
            self.favorite.disconnect(self.__on_favorite)
            self.removedFavorite.disconnect(self.__on_unfavorite)
        elif not favorite_category and active:
            category = EmojiCategory("Favorites", self._translations["Favorites"], self._icons["Favorites"])
            self.addCategory(category, 0, 0)
            self.favorite.connect(self.__on_favorite)
            self.removedFavorite.connect(self.__on_unfavorite)
        self.__favorite_category = active

    def setRecentCategory(self, active: bool):
        recent_category = self.category("Recent")
        if recent_category and not active:
            self.removeCategory(recent_category)
            self.picked.disconnect(self.__add_recent)
        elif not recent_category and active:
            category = EmojiCategory("Recent", self._translations["Recent"], self._icons["Recent"])
            self.addCategory(category, 0, 0)
            grid = category.grid()
            grid.setLimit(50)
            grid.setLimitTreatment(QEmojiGrid.LimitTreatment.RemoveFirstOne)
            self.picked.connect(self.__add_recent)
        self.__recent_category = active