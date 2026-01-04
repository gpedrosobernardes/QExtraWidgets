import sys

import qtawesome
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QGuiApplication
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QToolButton, QFrame, QGroupBox
)

from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.utils import is_dark_mode


class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QThemeResponsiveIcon Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))
        self.resize(600, 500)

        # --- UI Configuration ---
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # 1. Theme Control Section
        btn_theme_toggle = QPushButton("Toggle Theme (Light / Dark)")
        btn_theme_toggle.setFixedHeight(40)
        btn_theme_toggle.setIconSize(QSize(40, 40))
        # A simple icon for the theme button
        btn_theme_toggle.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.palette"))
        btn_theme_toggle.clicked.connect(self.toggleTheme)


        main_layout.addWidget(btn_theme_toggle)

        # Visual separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        # 2. Standard Icons Section (QtAwesome direct)
        group_standard = QGroupBox("Standard Icons (QtAwesome -> QAutoIcon)")
        layout_standard = QHBoxLayout()

        # Normal Button
        btn_rocket = QPushButton("Normal Button")
        btn_rocket.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.rocket"))
        btn_rocket.setIconSize(QSize(32, 32))

        # ToolButton (Flat)
        btn_gear = QToolButton()
        btn_gear.setText("Flat ToolButton")
        btn_gear.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.gear"))
        btn_gear.setIconSize(QSize(32, 32))
        btn_gear.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        btn_gear.setAutoRaise(True)

        # Disabled Button (Important test to see 'Disabled' color)
        btn_disabled = QPushButton("Disabled")
        btn_disabled.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.ban"))
        btn_disabled.setIconSize(QSize(32, 32))
        btn_disabled.setEnabled(False)

        layout_standard.addWidget(btn_rocket)
        layout_standard.addWidget(btn_gear)
        layout_standard.addWidget(btn_disabled)
        group_standard.setLayout(layout_standard)
        main_layout.addWidget(group_standard)

        # 3. Multi-Pixmap Test Section (States)
        group_multistate = QGroupBox("Multi-State Icon (On/Off)")
        layout_multistate = QVBoxLayout()

        lbl_info = QLabel("This button changes icon when clicked (Checked/Unchecked).\n"
                          "Both icons (empty and checked) should follow the theme color.")
        lbl_info.setStyleSheet("color: gray; font-style: italic; margin-bottom: 10px;")

        # --- MULTI-STATE ICON CREATION ---
        # Step A: Create a normal base QIcon
        base_multi_icon = QIcon()

        # Step B: Generate pixmaps for states using qtawesome
        # Note: We use neutral 'black' color, as QAutoIcon will overwrite the color.

        # OFF State (Normal, Off): Empty square ("fa6r.square" - regular style)
        pix_off = qtawesome.icon("fa6s.square", color="black").pixmap(QSize(48, 48))
        base_multi_icon.addPixmap(pix_off, QIcon.Mode.Normal, QIcon.State.Off)

        # ON State (Normal, On): Checked square ("fa6s.square-check" - solid style)
        pix_on = qtawesome.icon("fa6s.square-check", color="black").pixmap(QSize(48, 48))
        base_multi_icon.addPixmap(pix_on, QIcon.Mode.Normal, QIcon.State.On)

        # Step C: Wrap the base icon in our QAutoIcon
        # The engine now knows how to handle multiple internal states
        auto_multi_icon = QThemeResponsiveIcon(base_multi_icon)

        # Step D: Create the button that uses this icon
        self.btn_toggle_state = QPushButton("Click to Toggle State")
        self.btn_toggle_state.setFixedHeight(50)
        self.btn_toggle_state.setCheckable(True)  # Important!
        self.btn_toggle_state.setIcon(auto_multi_icon)
        self.btn_toggle_state.setIconSize(QSize(48, 48))

        # Connection just to change text for visual feedback
        self.btn_toggle_state.toggled.connect(self.updateToggleBtnText)

        layout_multistate.addWidget(lbl_info)
        layout_multistate.addWidget(self.btn_toggle_state)
        group_multistate.setLayout(layout_multistate)
        main_layout.addWidget(group_multistate)

        # Initialize with light theme
        self.applyLightTheme()

    def updateToggleBtnText(self, checked):
        state_text = "CHECKED (ON)" if checked else "UNCHECKED (OFF)"
        self.btn_toggle_state.setText(f"Click to Toggle State - {state_text}")

    def toggleTheme(self):
        """Toggles between palettes and applies to the entire application."""
        if is_dark_mode():
            self.applyLightTheme()
        else:
            self.applyDarkTheme()

    @staticmethod
    def applyDarkTheme():
        """Applies a generic dark palette."""
        QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Dark)

    @staticmethod
    def applyLightTheme():
        """Restores the default system palette (Light)."""
        # Using the default Fusion style palette is usually a clean light palette
        QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = DemoWindow()
    window.show()
    sys.exit(app.exec())