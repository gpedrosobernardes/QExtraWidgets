# QExtraWidgets

<p align="center">
  <img src="https://github.com/user-attachments/assets/4fa4f56a-6afc-434b-8478-4b750199f6d6" alt="QExtraWidgets Logo" width="600">
</p>

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

https://github.com/user-attachments/assets/821f9d80-ac9d-4503-9055-f70412ef8c7d

---

### 2. QEmojiPicker & QAwesomePicker

A full-featured Emoji and Icon Picker.

* **Rich Features:** Includes skin tone/color selector, favorites/recents management, and context menu actions (copy alias, favorite/unfavorite).
* **Optimized Search:** Fast filtering with recursive category matching.

https://github.com/user-attachments/assets/2992a3cb-133f-495d-8d55-649c0b37639a

https://github.com/user-attachments/assets/d159a659-2c32-4f3e-8c8d-735618a5d4de

---

### 3. QAccordion

A flexible accordion widget for grouping content in collapsible sections.

* **Customizable:** Change icon position (left/right) and animation speed.
* **Smooth Animation:** Uses `QPropertyAnimation` for expanding/collapsing.

https://github.com/user-attachments/assets/6c406347-a355-4a2a-b058-291a10a897c4

---

### 4. QThemeResponsiveIcon & QThemeResponsiveLabel

Stop worrying about Dark/Light mode icons. `QThemeResponsiveIcon` wraps `QtAwesome` to automatically invert colors (Black <-> White) based on the current system or application palette.

For labels, `QThemeResponsiveLabel` automatically updates its pixmap when the icon theme or widget size changes.

https://github.com/user-attachments/assets/e1439bc9-089d-4621-8597-850af43f6f99


---

### 5. Other Useful Widgets

| Widget                    | Description                                                                                                        | Image                                                                                                                            |
|---------------------------|--------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| **QPasswordLineEdit**     | A line edit with a built-in eye icon to toggle password visibility.                                                | ![QPasswordLineEdit](https://github.com/user-attachments/assets/5eef9d4b-e61d-4af2-b87c-bb62a821aac2)                            |
| **QPager**                | A classic pagination control for navigating large datasets.                                                        | ![QPager](https://github.com/user-attachments/assets/e8ec0e97-bb65-4828-aacc-3b38cd61fc63)                                       |
| **QColorButton**          | A button that allows setting custom background colors for different states (Normal, Hover, Pressed, Checked).      | ![QColorButton](https://github.com/user-attachments/assets/b7a5d400-5864-4b65-a8d4-cce951e09426)                                 |
| **QColorToolButton**      | A tool button that allows setting custom background colors for different states (Normal, Hover, Pressed, Checked). |                                                                                                                                  |
| **QDualList**             | Two lists side-by-side for moving items (Select/Deselect).                                                         | ![QDualList](https://github.com/user-attachments/assets/3fa65713-8c2c-46db-8037-e248fe9721bb)                                    |
| **QSearchLineEdit**       | A search input field with a clear button and search icon.                                                          | ![QSearchLineEdit](https://github.com/user-attachments/assets/cc553dea-5c60-4f32-9cfb-31fb57f36b62)                              |
| **QIconComboBox**         | A ToolButton-style combo box optimized for icons or short text.                                                    |                                                                                                                                  |
| **QEmojiPickerMenu**      | A menu wrapper for `QEmojiPicker` to easily attach it to buttons.                                                  |                                                                                                                                  |
| **QThemeResponsiveLabel** | A label that automatically updates its icon based on theme and size.                                               |                                                                                                                                  |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
