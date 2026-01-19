# API Reference

This page contains the automatic API reference for the `qextrawidgets` package.

## Widgets

The main widgets of the library.

::: qextrawidgets.widgets.accordion
::: qextrawidgets.widgets.accordion_item
::: qextrawidgets.widgets.color_button
::: qextrawidgets.widgets.dual_list
::: qextrawidgets.widgets.extra_text_edit
::: qextrawidgets.widgets.icon_combo_box
::: qextrawidgets.widgets.pager
::: qextrawidgets.widgets.password_line_edit
::: qextrawidgets.widgets.search_line_edit
::: qextrawidgets.widgets.theme_responsive_label
::: qextrawidgets.widgets.twemoji_text_edit

### Emoji Picker

::: qextrawidgets.widgets.emoji_picker.emoji_picker
::: qextrawidgets.widgets.emoji_picker.emoji_grid
::: qextrawidgets.widgets.emoji_picker.emoji_model

The QEmojiSortFilterProxyModel supports an injectable pixmap getter via `setEmojiPixmapGetter`. The getter may return either a QPixmap or a QIcon; the proxy converts QPixmap to QIcon for DecorationRole to ensure consistent native rendering. If the getter returns an invalid value, the model provides an empty QIcon.

### Filterable Table

::: qextrawidgets.widgets.filterable_table.filterable_table

## Delegates

::: qextrawidgets.delegates.standard_twemoji_delegate

## Proxies

::: qextrawidgets.proxys.emoji_sort_filter
::: qextrawidgets.proxys.multi_filter

## Validators

::: qextrawidgets.validators.emoji_validator

## Documents

::: qextrawidgets.documents.twemoji_text_document

## Utilities and Icons

::: qextrawidgets.icons
::: qextrawidgets.utils
::: qextrawidgets.emoji_utils
