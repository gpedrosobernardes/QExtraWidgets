import sys

from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QHBoxLayout,
)

from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.widgets.buttons.color_button import QColorButton
from qextrawidgets.widgets.buttons.color_tool_button import QColorToolButton


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(300, 400)

        self.setWindowTitle("QColorButton Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        self._init_widgets()
        self.setup_layout()
        self.setup_connections()

    def _init_widgets(self) -> None:
        # 1. Standard Buttons
        self.color_button_1 = QColorButton("#0077B6", "Color Button 1 (Blue)")
        self.color_button_2 = QColorButton("#CC2936", "Color Button 2 (Red)")
        self.color_button_3 = QColorButton(
            "#C5D86D", "Color Button 3 (Custom Text)", "#000000"
        )

        # 2. Toggle Button (Checked Color)
        # Create a checkable button with distinct colors for Normal and Checked states
        self.toggle_btn = QColorButton(
            "#0077B6",  # Normal Color (Blue)
            "Click to Toggle (Blue)",
            checked_color="#CC2936",  # Checked Color (Red)
        )
        self.toggle_btn.setCheckable(True)

        # 3. Tool Buttons
        self.color_tool_button_1 = QColorToolButton("#0077B6", "Tool Button 1 (Blue)")
        self.color_tool_button_1.setIcon(
            QThemeResponsiveIcon.fromAwesome("fa6s.droplet")
        )

        self.color_tool_button_2 = QColorToolButton("#CC2936", "Tool Button 2 (Red)")
        self.color_tool_button_2.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.fire"))

        self.color_tool_button_3 = QColorToolButton(
            "#C5D86D", "Tool Button 3 (Custom Text)", "#000000"
        )
        self.color_tool_button_3.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.leaf"))

        # 4. Toggle Tool Button
        self.toggle_tool_btn = QColorToolButton(
            "#2A9D8F",  # Normal (Green)
            "Play",
            checked_color="#E9C46A",  # Checked (Orange)
        )
        self.toggle_tool_btn.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.play"))
        self.toggle_tool_btn.setCheckable(True)

    def setup_layout(self) -> None:
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 1. Standard Buttons Group
        group_standard = QGroupBox("Standard Buttons")
        layout_standard = QVBoxLayout(group_standard)
        layout_standard.setSpacing(10)

        layout_standard.addWidget(
            QLabel("Basic color buttons with automatic text contrast:")
        )
        layout_standard.addWidget(self.color_button_1)
        layout_standard.addWidget(self.color_button_2)
        layout_standard.addWidget(self.color_button_3)

        main_layout.addWidget(group_standard)

        # 2. Toggle Button Group
        group_toggle = QGroupBox("Dynamic State")
        layout_toggle = QVBoxLayout(group_toggle)
        layout_toggle.setSpacing(10)

        layout_toggle.addWidget(
            QLabel("Toggle button changing color based on state (Blue <-> Red):")
        )
        layout_toggle.addWidget(self.toggle_btn)

        main_layout.addWidget(group_toggle)

        # 3. Tool Buttons Group
        group_tool = QGroupBox("Tool Buttons")
        layout_tool = QVBoxLayout(group_tool)
        layout_tool.setSpacing(10)

        layout_tool.addWidget(QLabel("Compact tool buttons with custom colors:"))

        # Use a horizontal layout for tool buttons to look like a toolbar
        h_layout_tool = QHBoxLayout()
        h_layout_tool.setSpacing(10)
        h_layout_tool.addWidget(self.color_tool_button_1)
        h_layout_tool.addWidget(self.color_tool_button_2)
        h_layout_tool.addWidget(self.color_tool_button_3)
        h_layout_tool.addSpacing(20)
        h_layout_tool.addWidget(self.toggle_tool_btn)
        h_layout_tool.addStretch()

        layout_tool.addLayout(h_layout_tool)

        main_layout.addWidget(group_tool)

        # Spacer to push everything up
        main_layout.addStretch()

        self.setCentralWidget(widget)

    def setup_connections(self) -> None:
        self.toggle_btn.toggled.connect(self.on_toggle)
        self.toggle_tool_btn.toggled.connect(self.on_tool_toggle)

    def on_tool_toggle(self, checked: bool):
        if checked:
            self.toggle_tool_btn.setText("Pause")
            self.toggle_tool_btn.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.pause"))
        else:
            self.toggle_tool_btn.setText("Play")
            self.toggle_tool_btn.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.play"))

    def on_toggle(self, checked: bool):
        if checked:
            self.toggle_btn.setText("Checked (Red)")
        else:
            self.toggle_btn.setText("Unchecked (Blue)")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
