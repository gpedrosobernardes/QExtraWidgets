# QExtraWidgets

**QExtraWidgets** is a comprehensive library of modern, responsive, and feature-rich widgets for **PySide6** applications. It aims to fill the gaps in standard Qt widgets by providing high-level components like Excel-style filterable tables, emoji pickers, accordion menus, and theme-aware icons.

---

## 📦 Installation

```bash
pip install qextrawidgets
```

**Requirements:**

* Python 3.8+
* PySide6 >= 6.10.1
* QtAwesome
* Emojis
* Twemoji-API

---

## ✨ Features & Widgets

### 1. QFilterableTable

A powerful `QTableView` extension that adds Excel-like filtering capabilities to headers.

* **Cascading Filters:** Filter options update based on other columns (drill-down).
* **Sort & Search:** Built-in sorting and search within the filter popup.
* **Model Agnostic:** Works with `QSqlTableModel`, `QStandardItemModel`, or any custom model.

![QFilterableTable](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QFilterableTable.png)

---

### 2. QEmojiPicker & Responsive Text Edit

A full-featured Emoji Picker and a Text Edit that renders Twemoji images inline.

* **Lazy Loading:** Efficiently handles thousands of emojis.
* **Auto-Resize:** The `QExtraTextEdit` grows automatically with content (like WhatsApp/Telegram).
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

### 4. QThemeResponsiveIcon

Stop worrying about Dark/Light mode icons. This class wraps `QtAwesome` to automatically invert colors (Black <-> White) based on the current system or application palette.

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

```python
from qextrawidgets.delegates.standard_twemoji_delegate import QStandardTwemojiDelegate

view = QListView()
delegate = QStandardTwemojiDelegate(view)
view.setItemDelegate(delegate)
```

---

### 6. Other Useful Widgets

| Widget                | Description | Image                                                                                                                            |
|-----------------------| --- |----------------------------------------------------------------------------------------------------------------------------------|
| **QPasswordLineEdit** | A line edit with a built-in eye icon to toggle password visibility. | ![QPasswordLineEdit](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QPasswordLineEdit.png) |
| **QPager**            | A classic pagination control for navigating large datasets. | ![QPager](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QPager.png)                       |
| **QColorButton**      | A button that displays a selected color and opens a dialog on click. | ![QColorButton](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QColorButton.png)           |
| **QDualList**         | Two lists side-by-side for moving items (Select/Deselect). | ![QDualList](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QDualList.png)                 |
| **QSearchLineEdit**   | A search input field with a clear button and search icon. | ![QSearchLineEdit](https://raw.githubusercontent.com/gpedrosobernardes/QExtraWidgets/main/assets/images/QSearchLineEdit.png)     |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
