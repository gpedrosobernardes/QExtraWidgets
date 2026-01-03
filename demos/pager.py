import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QGroupBox, QFormLayout, QSpinBox, QLabel, \
    QFrame

from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.widgets.pager import QPager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.setWindowTitle("QPager Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))
        self.resize(700, 500)

        # --- Interface Construction (Directly in __init__) ---

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)

        # 1. Configuration Panel
        config_group = QGroupBox("Pager Settings")
        form_layout = QFormLayout(config_group)

        self._spin_total_pages = QSpinBox()
        self._spin_total_pages.setRange(1, 1000)
        self._spin_total_pages.setValue(20)

        self._spin_visible_buttons = QSpinBox()
        self._spin_visible_buttons.setRange(1, 15)
        self._spin_visible_buttons.setValue(5)
        self._spin_visible_buttons.setToolTip("How many buttons appear at a time")

        form_layout.addRow("Total Pages:", self._spin_total_pages)
        form_layout.addRow("Visible Buttons:", self._spin_visible_buttons)

        # 2. Content Area
        self._content_label = QLabel("Page 1 Content")
        self._content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._content_label.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        font = QFont()
        font.setPixelSize(20)
        self._content_label.setFont(font)

        # 3. The Pager
        self._pager = QPager()
        self._pager.setTotalPages(20)
        self._pager.setVisibleButtonCount(5)

        # Add to main layout
        main_layout.addWidget(config_group)
        main_layout.addWidget(self._content_label, stretch=1)
        main_layout.addWidget(self._pager, stretch=0)

        # --- Connections ---
        self._spin_total_pages.valueChanged.connect(self._pager.setTotalPages)
        self._spin_visible_buttons.valueChanged.connect(self._pager.setVisibleButtonCount)
        self._pager.currentPageChanged.connect(self.__update_content)

    def __update_content(self, page_number):
        self._content_label.setText(f"Showing data for Page {page_number}\n(Total: {self._pager.totalPages()})")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
