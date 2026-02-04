# QExtraWidgets

[![PyPI version](https://badge.fury.io/py/qextrawidgets.svg)](https://badge.fury.io/py/qextrawidgets)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/qextrawidgets.svg)](https://pypi.org/project/qextrawidgets/)
[![Documentation Status](https://img.shields.io/badge/docs-stable-blue.svg)](https://gpedrosobernardes.github.io/QExtraWidgets/)

**QExtraWidgets** is a comprehensive library of modern, responsive, and feature-rich widgets for **PySide6** applications. It aims to fill the gaps in standard Qt widgets by providing high-level components like Excel-style filterable tables, emoji pickers, accordion menus, and theme-aware icons.


## 📖 Documentation

The complete documentation is available at: [https://gpedrosobernardes.github.io/QExtraWidgets/](https://gpedrosobernardes.github.io/QExtraWidgets/)


## 📦 Installation

```bash
pip install qextrawidgets
```


## ✨ Features & Widgets

### 1. QFilterableTable

A powerful `QTableView` extension that adds Excel-like filtering capabilities to headers.

* **Cascading Filters:** Filter options update based on other columns (drill-down).
* **Sort & Search:** Built-in sorting and search within the filter popup.
* **Model Agnostic:** Works with `QSqlTableModel`, `QStandardItemModel`, or any custom model.

![QFilterableTable](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QFilterableTable.png)

---

### 2. QEmojiPicker & QTwemojiTextEdit

A full-featured Emoji Picker and a Text Edit that renders Twemoji images inline.

* **Rich Features:** Includes skin tone selector, favorites/recents management, and context menu actions (copy alias, favorite/unfavorite).
* **Optimized Search:** Fast filtering with recursive category matching.
* **QTwemojiTextEdit:** Inherits from `QExtraTextEdit`, providing auto-resize capabilities (like WhatsApp/Telegram) while rendering high-quality Twemoji images.
* **Emoji Replacement:** Automatically converts `:smile:` aliases or pasted unicode characters into high-quality images.

![QEmojiPicker](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QEmojiPicker.png)
![QExtraTextEdit](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QExtraTextEdit.png)

---

### 3. QAccordion

A flexible accordion widget for grouping content in collapsible sections.

* **Customizable:** Change icon position (left/right) and animation speed.
* **Smooth Animation:** Uses `QPropertyAnimation` for expanding/collapsing.

![QAccordion](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QAccordion.png)

---

### 4. QThemeResponsiveIcon & QThemeResponsiveLabel

Stop worrying about Dark/Light mode icons. `QThemeResponsiveIcon` wraps `QtAwesome` to automatically invert colors (Black <-> White) based on the current system or application palette.

For labels, `QThemeResponsiveLabel` automatically updates its pixmap when the icon theme or widget size changes.

```python
from qextrawidgets.icons import QThemeResponsiveIcon
from PySide6.QtWidgets import QPushButton

btn = QPushButton("Theme Aware Button")
# Automatically switches color when QPalette changes
btn.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.house"))

```

---

### 5. QStandardTwemojiDelegate

A delegate that renders Twemoji images within standard item views (like `QListView`, `QTableView`, `QTreeView`).

* **Unicode Support:** Renders standard Unicode emojis as high-quality Twemoji images.
* **Alignment:** Supports standard Qt text alignment flags.
* **Mixed Content:** Handles text mixed with emojis seamlessly.

![QStandardTwemojiDelegate](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QStandardTwemojiDelegate.png)

```python
from PySide6.QtWidgets import QListView
from qextrawidgets.delegates.standard_twemoji_delegate import QStandardTwemojiDelegate

view = QListView()
delegate = QStandardTwemojiDelegate(view)
view.setItemDelegate(delegate)
```

---

### 6. Other Useful Widgets

| Widget                | Description                                                          | Image                                                                                                                            |
|-----------------------|----------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| **QPasswordLineEdit** | A line edit with a built-in eye icon to toggle password visibility.  | ![QPasswordLineEdit](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QPasswordLineEdit.png) |
| **QPager**            | A classic pagination control for navigating large datasets.          | ![QPager](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QPager.png)                       |
| **QColorButton**      | A button that allows setting custom background colors for different states (Normal, Hover, Pressed, Checked). | ![QColorButton](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QColorButton.png)           |
| **QColorToolButton**  | A tool button that allows setting custom background colors for different states (Normal, Hover, Pressed, Checked). |                                                                                                                                  |
| **QDualList**         | Two lists side-by-side for moving items (Select/Deselect).           | ![QDualList](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QDualList.png)                 |
| **QSearchLineEdit**   | A search input field with a clear button and search icon.            | ![QSearchLineEdit](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QSearchLineEdit.png)     |
| **QIconComboBox**     | A ToolButton-style combo box optimized for icons or short text.      |                                                                                                                                  |
| **QEmojiPickerMenu**  | A menu wrapper for `QEmojiPicker` to easily attach it to buttons.    |                                                                                                                                  |
| **QThemeResponsiveLabel** | A label that automatically updates its icon based on theme and size. |                                                                                                                                  |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
