import logging
import time
import typing
import urllib

from PySide6.QtCore import QSize, QTimer, Slot, QPoint, QPersistentModelIndex, QModelIndex, Signal, QUrlQuery, \
    QThreadPool, QElapsedTimer
from PySide6.QtGui import Qt, QFont, QPixmap, QIcon, QFontMetrics, QStandardItem, QImage
from PySide6.QtWidgets import QWidget, QAbstractItemView, QButtonGroup, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, \
    QMenu, QApplication, QToolButton
from pygments.lexers import func

from qextrawidgets.core.runnables.image_provider import QImageProviderSignals
from qextrawidgets.core.utils.system_utils import log_qt_performance
from qextrawidgets.gui.items import QIconCategoryItem
from qextrawidgets.gui.models.icon_picker_model import QIconPickerModel
from qextrawidgets.gui.proxys.icon_picker_proxy import QIconPickerProxyModel
from qextrawidgets.widgets.delegates import QGroupedIconDelegate
from qextrawidgets.widgets.inputs import QIconComboBox, QSearchLineEdit
from qextrawidgets.widgets.views import QGroupedIconView


class QIconPicker(QWidget):
    """A generic icon picker widget.

    Features categories, search, recent and favorites.

    Signals:
        picked: Emitted when a QIcon item is clicked.
    """

    picked = Signal(QStandardItem)

    def __init__(self,
                 image_provider: typing.Type[QImageProviderSignals],
                 model: QIconPickerModel,
                 parent: typing.Optional[QWidget] = None,
                 icon_label_size: int = 32,
                 alias_format: str = "{alias}") -> None:
        super().__init__(parent)

        self._pool = QThreadPool()
        self._pool.setExpiryTimeout(-1)
        self._pool.setMaxThreadCount(1)

        self._images = {}

        self._image_provider = image_provider

        self._alias_format = alias_format

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(200)

        self._model = model
        self._proxy = QIconPickerProxyModel()
        self._proxy.setSourceModel(self._model)

        self._search_line_edit = self._create_search_line_edit()

        self._color_modifier_selector = QIconComboBox()

        self._grouped_icon_view = QGroupedIconView(self, QSize(40, 40), 5)
        self._grouped_icon_view.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self._grouped_icon_view.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )
        self._grouped_icon_view.setModel(self._proxy)

        self._shortcuts_container = QWidget()
        self._shortcuts_container.setFixedHeight(40)  # Fixed height for the bar

        self._shortcuts_group = QButtonGroup(self)
        self._shortcuts_group.setExclusive(True)

        self._icon_label = QLabel()
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setScaledContents(True)
        self._icon_label.setFixedSize(icon_label_size, icon_label_size)

        self._aliases_icon_label = self._create_icon_label()

        self.setContentsMargins(10, 10, 10, 10)

        self._setup_layout()
        self._setup_connections()

        self._on_model_reset()

    # Private methods
    @staticmethod
    def _create_icon_label() -> QLabel:
        """Creates and configures the emoji alias label.

        Returns:
            QLabel: The configured alias label.
        """
        font = QFont()
        font.setBold(True)
        font.setPointSize(13)

        label = QLabel()
        label.setFont(font)
        return label

    @staticmethod
    def _create_search_line_edit() -> QLineEdit:
        """Creates and configures a search line edit.

        Returns:
            QLineEdit: The configured search line edit.
        """
        font = QFont()
        font.setPointSize(12)

        line_edit = QSearchLineEdit()
        line_edit.setFont(font)
        return line_edit

    @staticmethod
    def _create_shortcut_button(text: str, icon: QIcon) -> QToolButton:
        """Creates a shortcut button for the category bar.

        Args:
            text (str): Tooltip text.
            icon (QIcon): Button icon.

        Returns:
            QToolButton: The configured shortcut button.
        """
        btn = QToolButton()
        btn.setCheckable(True)
        btn.setAutoRaise(True)
        btn.setFixedSize(32, 32)
        btn.setIconSize(QSize(22, 22))
        btn.setToolTip(text)
        btn.setText(text)
        btn.setIcon(icon)
        return btn

    def _setup_layout(self) -> None:
        """Sets up the initial layout of the widget."""
        self._shortcuts_layout = QHBoxLayout(self._shortcuts_container)
        self._shortcuts_layout.setContentsMargins(5, 0, 5, 0)
        self._shortcuts_layout.setSpacing(2)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self._search_line_edit, True)
        header_layout.addWidget(self._color_modifier_selector)

        content_layout = QHBoxLayout()
        content_layout.addWidget(self._icon_label)
        content_layout.addWidget(self._aliases_icon_label, True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self._shortcuts_container)
        main_layout.addWidget(self._grouped_icon_view)
        main_layout.addLayout(content_layout)

    def _setup_connections(self) -> None:
        """Sets up signals and slots connections."""
        self._search_timer.timeout.connect(self._on_filter_emojis)
        self._search_line_edit.textChanged.connect(lambda: self._search_timer.start())

        self._grouped_icon_view.itemEntered.connect(self._on_mouse_entered_icon)
        self._grouped_icon_view.itemExited.connect(self._on_mouse_exited_emoji)
        self._grouped_icon_view.itemClicked.connect(self._on_item_clicked)
        self._grouped_icon_view.customContextMenuRequested.connect(
            self._on_context_menu
        )

        self._model.categoryInserted.connect(self._on_categories_inserted)
        self._model.categoryRemoved.connect(self._on_categories_removed)

        self._color_modifier_selector.currentDataChanged.connect(self._on_set_color_modifier)

        delegate: QGroupedIconDelegate = self._grouped_icon_view.itemDelegate()
        delegate.requestImage.connect(self._on_request_image)

    @Slot(QStandardItem)
    def _on_set_color_modifier(self, icon_item: QStandardItem) -> None:
        """Updates the skin tone of the emojis.

        Args:
            icon_item (QIconItem): QIconItem instance representing the color_modifier.
        """
        pass

    # Connections
    @Slot(QPoint)
    def _on_context_menu(self, position: QPoint) -> None:
        """Handles the context menu for an icon.

        Args:
            position (QPoint): Pixel position where the context menu was requested.
        """
        proxy_index = self._grouped_icon_view.indexAt(position)
        source_index = self._proxy.mapToSource(proxy_index)
        item = self._model.itemFromIndex(source_index)
        parent = item.parent()

        menu = QMenu(self._grouped_icon_view)

        if parent is None:
            collapse_all_action = menu.addAction(self.tr("Collapse all"))
            collapse_all_action.triggered.connect(self._grouped_icon_view.collapseAll)
            expand_all_action = menu.addAction(self.tr("Expand all"))
            expand_all_action.triggered.connect(self._grouped_icon_view.expandAll)

        else:
            icon_text = item.data(Qt.ItemDataRole.EditRole)

            # Check if emoji exists in favorites using helper method
            favorite_item = self._model.findIconInCategoryByName(
                QIconPickerModel.BaseCategory.Favorites, icon_text
            )

            if favorite_item:
                action = menu.addAction(self.tr("Unfavorite"))
                action.triggered.connect(
                    lambda: self._model.removeIcon(QIconPickerModel.BaseCategory.Favorites, icon_text)
                )
            else:
                action = menu.addAction(self.tr("Favorite"))
                # We use item.emojiChar() here because addEmoji expects an EmojiChar object
                action.triggered.connect(
                    lambda: self._model.addIcon(QIconPickerModel.BaseCategory.Favorites, item.clone())
                )

            copy_alias_action = menu.addAction(self.tr("Copy alias"))
            clipboard = QApplication.clipboard()
            aliases = item.data(Qt.ItemDataRole.UserRole)

            alias = aliases[0] if aliases else item.data(Qt.ItemDataRole.EditRole)
            copy_alias_action.triggered.connect(lambda: clipboard.setText(alias))

        menu.exec(self._grouped_icon_view.mapToGlobal(position))

    def _build_url_query(self, index: typing.Union[QPersistentModelIndex, QModelIndex], size: QSize) -> QUrlQuery:
        pass

    @log_qt_performance
    @Slot(QPersistentModelIndex, QSize, float)
    def _on_request_image(self, persistent_index: QPersistentModelIndex, size: QSize) -> None:
        timer = QElapsedTimer()
        timer.start()
        url_query = self._build_url_query(persistent_index, size)
        url_query_string = url_query.toString()
        logging.debug(f"Build url query in {timer.elapsed()} ms.")

        try:
            image: typing.Optional[QImage] = self._images[url_query_string]
        except KeyError:
            self._images[url_query_string] = None
            timer = QElapsedTimer()
            timer.start()
            provider = self._image_provider(url_query)
            logging.debug(f"Created provider in {timer.elapsed()} ms.")
            provider.success.connect(self._on_request_image_success)
            self._pool.start(provider)
        else:
            if image is not None:
                model_index = self._proxy.mapToSource(persistent_index)
                item = self._model.itemFromIndex(model_index)
                item.setData(image, Qt.ItemDataRole.DecorationRole)

    def _on_request_image_success(self, url_query: QUrlQuery, image: QImage) -> None:
        url_query_string = url_query.toString()
        self._images[url_query_string] = image

    @Slot(QModelIndex)
    def _on_shortcut_clicked(self, source_index: QModelIndex) -> None:
        """Scrolls the view to the selected category section.

        Args:
            source_index (QModelIndex): The index of the category in the source model.
        """
        proxy_index = self._proxy.mapFromSource(source_index)
        self._grouped_icon_view.scrollTo(proxy_index)
        self._grouped_icon_view.setExpanded(QPersistentModelIndex(proxy_index), True)

    @Slot(QStandardItem)
    def _on_categories_inserted(self, category_item: QStandardItem) -> None:
        """Handles the insertion of categories into the model.

        Args:
            category_item (QIconCategoryItem): The inserted category item.
        """
        category = category_item.text()
        icon = category_item.icon()

        shortcut = self._create_shortcut_button(category, icon)
        shortcut.setObjectName(category)
        shortcut.clicked.connect(
            lambda: self._on_shortcut_clicked(category_item.index())
        )

        self._shortcuts_layout.addWidget(shortcut)
        self._shortcuts_group.addButton(shortcut)

    @Slot(QStandardItem)
    def _on_categories_removed(self, category_item: QStandardItem) -> None:
        """Handles the removal of categories into the model.

        Args:
            category_item (QIconCategoryItem): The removed category item.
        """
        category = category_item.data(Qt.ItemDataRole.UserRole)
        button = self._shortcuts_container.findChild(QToolButton, category)

        if button:
            self._shortcuts_layout.removeWidget(button)
            self._shortcuts_group.removeButton(button)
            button.deleteLater()

    @Slot()
    def _on_model_reset(self):
        """Handles the reset of the model."""
        for button in self._shortcuts_group.buttons():
            self._shortcuts_layout.removeWidget(button)
            self._shortcuts_group.removeButton(button)
            button.deleteLater()

        for row in range(self._model.rowCount()):
            item = self._model.item(row)
            if isinstance(item, QStandardItem):
                self._on_categories_inserted(item)

    @Slot(QModelIndex)
    def _on_mouse_entered_icon(self, index: QModelIndex) -> None:
        """Handles mouse entry events on emoji items to show preview.

        Args:
            index (QModelIndex): The index of the item under the mouse.
        """
        source_index = self._proxy.mapToSource(index)
        item = self._model.itemFromIndex(source_index)
        if item.parent():
            url_query = self._build_url_query(index, self._icon_label.size())

            cached = self._images.get(url_query.toString())
            if isinstance(cached, QImage):
                self._icon_label.setPixmap(QPixmap.fromImage(cached))
            else:
                provider = self._image_provider(url_query)
                provider.success.connect(self._on_label_image_received)
                self._pool.start(provider)

            aliases = item.data(Qt.ItemDataRole.UserRole)
            aliases_text = " ".join(self._alias_format.format(alias=alias) for alias in aliases)

            metrics = QFontMetrics(self._aliases_icon_label.font())
            elided_alias = metrics.elidedText(
                aliases_text,
                Qt.TextElideMode.ElideRight,
                self._aliases_icon_label.width(),
            )
            self._aliases_icon_label.setText(elided_alias)

    def _on_label_image_received(self, url_query: QUrlQuery, image: QImage) -> None:
        pixmap = QPixmap.fromImage(image)
        self._icon_label.setPixmap(pixmap)
        self._images[url_query.toString()] = image

    @Slot()
    def _on_mouse_exited_emoji(self) -> None:
        """Clears the emoji preview area."""
        self._icon_label.clear()
        self._aliases_icon_label.clear()
        self._emoji_on_label = None

    @Slot(QModelIndex)
    def _on_item_clicked(self, proxy_index: QModelIndex) -> None:
        """Handles clicks on emoji items.

        Args:
            proxy_index (QModelIndex): The index in the proxy model that was clicked.
        """
        source_index = self._proxy.mapToSource(proxy_index)
        item = self._model.itemFromIndex(source_index)

        if isinstance(item, QIconCategoryItem):
            return

        self.picked.emit(item)

        recent_category_item = self._model.findCategory(QIconPickerModel.BaseCategory.Recents)

        if recent_category_item:
            self._model.addIcon(QIconPickerModel.BaseCategory.Recents, item.clone())

    @Slot()
    def _on_filter_emojis(self) -> None:
        """Filters the emojis across all categories based on the search text."""
        text = self._search_line_edit.text()
        self._proxy.setFilterFixedString(text)

    def translateUI(self) -> None:
        """Translates the UI components."""
        self._search_line_edit.setPlaceholderText(self.tr("Search emoji..."))

    def resetPicker(self) -> None:
        """Resets the picker state."""
        self._search_line_edit.clear()

    def delegate(self) -> QGroupedIconDelegate:
        """Returns the item delegate used by the view."""
        return self._grouped_icon_view.itemDelegate()

    def view(self) -> QGroupedIconView:
        """Returns the internal grouped icon view."""
        return self._grouped_icon_view
