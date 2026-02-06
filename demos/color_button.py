import sys

from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QLabel

from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.widgets.buttons.color_button import QColorButton
from qextrawidgets.widgets.buttons.color_tool_button import QColorToolButton


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(300, 500)

        self.setWindowTitle("QColorButton Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        widget = QWidget()

        layout = QVBoxLayout()

        # 1. Standard Buttons
        layout.addWidget(QLabel("Standard Buttons:"))
        color_button_1 = QColorButton("#0077B6", "Color Button 1 (Blue)")
        color_button_2 = QColorButton("#CC2936", "Color Button 2 (Red)")
        color_button_3 = QColorButton("#C5D86D", "Color Button 3 (Custom Text)", "#000000")
        
        layout.addWidget(color_button_1)
        layout.addWidget(color_button_2)
        layout.addWidget(color_button_3)

        layout.addSpacing(20)

        # 2. Toggle Button (Checked Color)
        layout.addWidget(QLabel("Toggle Button (Blue <-> Red):"))
        
        # Create a checkable button with distinct colors for Normal and Checked states
        self.toggle_btn = QColorButton(
            "#0077B6", # Normal Color (Blue)
            "Click to Toggle (Blue)",
            checked_color="#CC2936" # Checked Color (Red)
        )
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.toggled.connect(self.on_toggle)
        
        layout.addWidget(self.toggle_btn)

        layout.addSpacing(20)

        # 3. Tool Buttons
        layout.addWidget(QLabel("Tool Buttons:"))
        color_tool_button_1 = QColorToolButton("#0077B6", "Tool Button 1 (Blue)")
        color_tool_button_2 = QColorToolButton("#CC2936", "Tool Button 2 (Red)")
        color_tool_button_3 = QColorToolButton("#C5D86D", "Tool Button 3 (Custom Text)", "#000000")

        layout.addWidget(color_tool_button_1)
        layout.addWidget(color_tool_button_2)
        layout.addWidget(color_tool_button_3)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def on_toggle(self, checked: bool):
        if checked:
            self.toggle_btn.setText("Checked (Red)")
        else:
            self.toggle_btn.setText("Unchecked (Blue)")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
