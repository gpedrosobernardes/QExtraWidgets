import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

from qextrawidgets.widgets.emoji_picker import QEmojiPicker


class SimpleEmojiPickerDemo(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Simple Emoji Picker Demo")
        self.resize(400, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)

        # Label to display the selected emoji
        self.result_label = QLabel("Select an emoji")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Using a larger font for the emoji display
        font = self.result_label.font()
        font.setPointSize(24)
        self.result_label.setFont(font)
        
        layout.addWidget(self.result_label)

        # Instantiate the Emoji Picker
        self.picker = QEmojiPicker()
        layout.addWidget(self.picker)

        # Connect the 'picked' signal to update the label
        self.picker.picked.connect(self._on_emoji_picked)

    def _on_emoji_picked(self, emoji: str) -> None:
        self.result_label.setText(f"Selected: {emoji}")


def main() -> None:
    app = QApplication(sys.argv)
    window = SimpleEmojiPickerDemo()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
