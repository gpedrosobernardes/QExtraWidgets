import sys

import qtawesome
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QToolButton,
    QFrame,
    QGroupBox,
)

from qextrawidgets.core.utils.system_utils import QSystemUtils
from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.widgets.displays.theme_responsive_label import QThemeResponsiveLabel


class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QThemeResponsiveIcon Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))
        self.resize(600, 500)

        self._init_widgets()
        self.setup_layout()
        self.setup_connections()

        # Initialize with light theme
        QSystemUtils.applyLightMode()

    def _init_widgets(self) -> None:
        # 1. Theme Control Section
        self.button_theme_toggle = QPushButton("Toggle Theme (Light / Dark)")
        self.button_theme_toggle.setFixedHeight(40)
        self.button_theme_toggle.setIconSize(QSize(40, 40))
        # A simple icon for the theme button
        self.button_theme_toggle.setIcon(
            QThemeResponsiveIcon.fromAwesome("fa6s.palette")
        )

        # Visual separator
        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        # 2. Standard Icons Section (QtAwesome direct)
        self.group_standard = QGroupBox("Standard Icons (QtAwesome -> QAutoIcon)")

        # Normal Button
        self.button_rocket = QPushButton("Normal Button")
        self.button_rocket.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.rocket"))
        self.button_rocket.setIconSize(QSize(32, 32))

        # ToolButton (Flat)
        self.button_gear = QToolButton()
        self.button_gear.setText("Flat ToolButton")
        self.button_gear.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.gear"))
        self.button_gear.setIconSize(QSize(32, 32))
        self.button_gear.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.button_gear.setAutoRaise(True)

        # Disabled Button (Important test to see 'Disabled' color)
        self.button_disabled = QPushButton("Disabled")
        self.button_disabled.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.ban"))
        self.button_disabled.setIconSize(QSize(32, 32))
        self.button_disabled.setEnabled(False)

        # 3. Multi-Pixmap Test Section (States)
        self.group_multistate = QGroupBox("Multi-State Icon (On/Off)")

        self.label_info = QLabel(
            "This button changes icon when clicked (Checked/Unchecked).\n"
            "Both icons (empty and checked) should follow the theme color."
        )
        self.label_info.setStyleSheet(
            "color: gray; font-style: italic; margin-bottom: 10px;"
        )

        # --- MULTI-STATE ICON CREATION ---
        # Step A: Create a normal base QIcon
        base_multi_icon = QIcon()

        # Step B: Generate pixmaps for states using qtawesome
        # Note: We use neutral 'black' color, as QAutoIcon will overwrite the color.

        # OFF State (Normal, Off): Empty square ("fa6r.square" - regular style)
        pixmap_off = qtawesome.icon("fa6s.square", color="black").pixmap(QSize(48, 48))
        base_multi_icon.addPixmap(pixmap_off, QIcon.Mode.Normal, QIcon.State.Off)

        # ON State (Normal, On): Checked square ("fa6s.square-check" - solid style)
        pixmap_on = qtawesome.icon("fa6s.square-check", color="black").pixmap(
            QSize(48, 48)
        )
        base_multi_icon.addPixmap(pixmap_on, QIcon.Mode.Normal, QIcon.State.On)

        # Step C: Wrap the base icon in our QAutoIcon
        # The engine now knows how to handle multiple internal states
        auto_multi_icon = QThemeResponsiveIcon(base_multi_icon)

        # Step D: Create the button that uses this icon
        self.button_toggle_state = QPushButton("Click to Toggle State")
        self.button_toggle_state.setFixedHeight(50)
        self.button_toggle_state.setCheckable(True)  # Important!
        self.button_toggle_state.setIcon(auto_multi_icon)
        self.button_toggle_state.setIconSize(QSize(48, 48))

        # 4. QThemeResponsiveLabel Section
        self.group_label = QGroupBox("QThemeResponsiveLabel")

        self.label_description = QLabel(
            "This QLabel automatically updates its pixmap when the theme changes or it is resized.\n"
            "Try resizing the window to see it in action."
        )
        self.label_description.setStyleSheet(
            "color: gray; font-style: italic; margin-bottom: 10px;"
        )

        self.responsive_label = QThemeResponsiveLabel()
        self.responsive_label.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.ghost"))
        # Set a minimum size so it's visible even without text
        self.responsive_label.setMinimumSize(64, 64)
        self.responsive_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def setup_layout(self) -> None:
        # --- UI Configuration ---
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # 1. Theme Control Section
        main_layout.addWidget(self.button_theme_toggle)
        main_layout.addWidget(self.line)

        # 2. Standard Icons Section (QtAwesome direct)
        layout_standard = QHBoxLayout()
        layout_standard.addWidget(self.button_rocket)
        layout_standard.addWidget(self.button_gear)
        layout_standard.addWidget(self.button_disabled)
        self.group_standard.setLayout(layout_standard)
        main_layout.addWidget(self.group_standard)

        # 3. Multi-Pixmap Test Section (States)
        layout_multistate = QVBoxLayout()
        layout_multistate.addWidget(self.label_info)
        layout_multistate.addWidget(self.button_toggle_state)
        self.group_multistate.setLayout(layout_multistate)
        main_layout.addWidget(self.group_multistate)

        # 4. QThemeResponsiveLabel Section
        layout_label = QVBoxLayout()
        layout_label.addWidget(self.label_description)
        layout_label.addWidget(self.responsive_label)
        self.group_label.setLayout(layout_label)
        main_layout.addWidget(self.group_label)

    def setup_connections(self) -> None:
        self.button_theme_toggle.clicked.connect(self.toggleTheme)
        # Connection just to change text for visual feedback
        self.button_toggle_state.toggled.connect(self.updateToggleButtonText)

    def updateToggleButtonText(self, checked):
        state_text = "CHECKED (ON)" if checked else "UNCHECKED (OFF)"
        self.button_toggle_state.setText(f"Click to Toggle State - {state_text}")

    @staticmethod
    def toggleTheme():
        """Toggles between palettes and applies to the entire application."""
        if QSystemUtils.isDarkMode():
            QSystemUtils.applyLightMode()
        else:
            QSystemUtils.applyDarkMode()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = DemoWindow()
    window.show()
    sys.exit(app.exec())
