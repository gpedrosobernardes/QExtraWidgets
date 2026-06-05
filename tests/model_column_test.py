"""
Tests for modelColumn / setModelColumn behaviour in QEmojiView.

Covers:
- Default value after construction
- Round-trip set/get
- Boundary values (zero, large index)
- Data is read from the correct column when requestImage fires
- Changing the column forces a full reload of the delegate cache
"""

import pytest
from unittest.mock import MagicMock, patch, call
from pytestqt.qtbot import QtBot

from PySide6.QtCore import Qt, QSize, QPersistentModelIndex
from PySide6.QtGui import QPixmap, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QApplication

from qextrawidgets.widgets.views.emoji_view import QEmojiView
from qextrawidgets.gui.items import QIconItem


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def view(qtbot: QtBot) -> QEmojiView:
    """A bare QEmojiView with a transparent pixmap getter (no network/disk I/O)."""
    def dummy_getter(item: QIconItem, size: QSize, dpr: float) -> QPixmap:
        px = QPixmap(size)
        px.fill(Qt.GlobalColor.transparent)
        px.setDevicePixelRatio(dpr)
        return px

    v = QEmojiView(icon_pixmap_getter=dummy_getter)
    qtbot.addWidget(v)
    return v


@pytest.fixture
def populated_model() -> QStandardItemModel:
    """
    A two-column model:
      col 0: "WRONG_EMOJI"
      col 1: "😀"  ← the emoji we actually want
    """
    model = QStandardItemModel(3, 2)
    for row in range(3):
        model.setItem(row, 0, QStandardItem("WRONG_EMOJI"))
        model.setItem(row, 1, QStandardItem("😀"))
    return model


# ---------------------------------------------------------------------------
# Default value
# ---------------------------------------------------------------------------

class TestModelColumnDefault:
    def test_default_is_zero(self, view: QEmojiView) -> None:
        """modelColumn() must return 0 immediately after construction."""
        assert view.modelColumn() == 0


# ---------------------------------------------------------------------------
# Round-trip set / get
# ---------------------------------------------------------------------------

class TestModelColumnSetGet:
    def test_set_then_get(self, view: QEmojiView) -> None:
        view.setModelColumn(1)
        assert view.modelColumn() == 1

    def test_set_zero_explicitly(self, view: QEmojiView) -> None:
        view.setModelColumn(3)
        view.setModelColumn(0)
        assert view.modelColumn() == 0

    def test_set_large_index(self, view: QEmojiView) -> None:
        view.setModelColumn(999)
        assert view.modelColumn() == 999

    def test_multiple_sets_last_wins(self, view: QEmojiView) -> None:
        view.setModelColumn(1)
        view.setModelColumn(5)
        view.setModelColumn(2)
        assert view.modelColumn() == 2


# ---------------------------------------------------------------------------
# Data is read from the correct column on requestImage
# ---------------------------------------------------------------------------

class TestModelColumnDataReading:
    def test_reads_emoji_from_correct_column(
        self,
        view: QEmojiView,
        populated_model: QStandardItemModel,
        qtbot: QtBot,
    ) -> None:
        """
        When modelColumn is 1, _on_request_image must read the emoji from
        column 1 ('😀') and NOT from column 0 ('WRONG_EMOJI').
        """
        received: list[str] = []

        def capturing_getter(item: QIconItem, size: QSize, dpr: float) -> QPixmap:
            received.append(item.data(Qt.ItemDataRole.EditRole))
            px = QPixmap(size)
            px.fill(Qt.GlobalColor.transparent)
            return px

        view.setIconPixmapGetter(capturing_getter)
        view.setModelColumn(1)

        # Wire the populated model through the proxy
        proxy = view.model()
        proxy.setSourceModel(populated_model)

        # Simulate a requestImage for row 0, column 1
        source_index = populated_model.index(0, 1)
        persistent = QPersistentModelIndex(proxy.mapFromSource(source_index))
        view._on_request_image(persistent, QSize(32, 32), 1.0)

        assert received == ["😀"], (
            f"Expected emoji '😀' from column 1, got {received}"
        )

    def test_wrong_column_reads_wrong_data(
        self,
        view: QEmojiView,
        populated_model: QStandardItemModel,
        qtbot: QtBot,
    ) -> None:
        """Sanity check: column 0 returns 'WRONG_EMOJI', not the emoji."""
        received: list[str] = []

        def capturing_getter(item: QIconItem, size: QSize, dpr: float) -> QPixmap:
            received.append(item.data(Qt.ItemDataRole.EditRole))
            return QPixmap()

        view.setIconPixmapGetter(capturing_getter)
        view.setModelColumn(0)

        proxy = view.model()
        proxy.setSourceModel(populated_model)

        source_index = populated_model.index(0, 0)
        persistent = QPersistentModelIndex(proxy.mapFromSource(source_index))
        view._on_request_image(persistent, QSize(32, 32), 1.0)

        assert received == ["WRONG_EMOJI"]


# ---------------------------------------------------------------------------
# Changing column forces delegate cache reload
# ---------------------------------------------------------------------------

class TestModelColumnForceReload:
    def test_set_column_calls_force_reload_all(self, view: QEmojiView) -> None:
        """
        setModelColumn must invalidate the delegate cache so items are
        re-requested with the new column on the next paint.
        """
        delegate = view.itemDelegate()
        delegate.forceReloadAll = MagicMock(wraps=delegate.forceReloadAll)

        view.setModelColumn(2)

        delegate.forceReloadAll.assert_called_once()

    def test_set_same_column_does_not_reload(self, view: QEmojiView) -> None:
        """
        Setting the same column value should be a no-op — no unnecessary
        cache invalidation or repaint.
        """
        view.setModelColumn(1)

        delegate = view.itemDelegate()
        delegate.forceReloadAll = MagicMock(wraps=delegate.forceReloadAll)

        view.setModelColumn(1)  # same value

        delegate.forceReloadAll.assert_not_called()