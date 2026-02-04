# API Reference

This page contains the automatic API reference for the `qextrawidgets` package.

## Widgets

The main widgets of the library.

::: qextrawidgets.widgets.accordion
::: qextrawidgets.widgets.accordion_item
::: qextrawidgets.widgets.color_button
::: qextrawidgets.widgets.color_tool_button
::: qextrawidgets.widgets.dual_list
::: qextrawidgets.widgets.extra_text_edit
::: qextrawidgets.widgets.icon_combo_box
::: qextrawidgets.widgets.pager
::: qextrawidgets.widgets.password_line_edit
::: qextrawidgets.widgets.search_line_edit
::: qextrawidgets.widgets.theme_responsive_label
::: qextrawidgets.widgets.twemoji_text_edit

### Emoji Picker

::: qextrawidgets.widgets.emoji_picker
::: qextrawidgets.widgets.emoji_picker_menu
::: qextrawidgets.models.emoji_picker_model

The `QEmojiPicker` widget (and by extension `QEmojiPickerMenu`) manages custom emoji rendering through its `setEmojiPixmapGetter` method. This allows you to inject a custom function, font, or logic to generate pixmaps for emojis, ensuring consistent visual representation across the picker's view and model. The picker ensures these pixmaps are correctly provided to the underlying model and delegates for display.

### Filterable Table

::: qextrawidgets.widgets.filterable_table.filterable_table

## Delegates

::: qextrawidgets.delegates.standard_twemoji_delegate
::: qextrawidgets.delegates.grouped_icon_delegate

## Proxies

::: qextrawidgets.proxys.emoji_picker_proxy
::: qextrawidgets.proxys.emoji_sort_filter
::: qextrawidgets.proxys.multi_filter

## Views

::: qextrawidgets.views.emoji_grid_view
::: qextrawidgets.views.filter_header_view
::: qextrawidgets.views.filterable_table_view
::: qextrawidgets.views.grouped_icon_view

## Items

::: qextrawidgets.items.emoji_category_item
::: qextrawidgets.items.emoji_item

## Validators

::: qextrawidgets.validators.emoji_validator

## Documents

::: qextrawidgets.documents.twemoji_text_document

## Utilities and Icons

::: qextrawidgets.icons
::: qextrawidgets.utils
::: qextrawidgets.emoji_utils
