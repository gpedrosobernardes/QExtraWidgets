from PySide6.QtWidgets import QPushButton

from widgets.utils import adjust_brightness


class QColorButton(QPushButton):
    def __init__(self, text: str, color: str, font_color: str = "white"):
        super().__init__()
        self.setText(text)
        hover_color = adjust_brightness(color, 15)
        pressed_color = adjust_brightness(color, -15)
        disabled_color = adjust_brightness(color, -30)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: %s;
                color: %s;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: %s;
            }
            QPushButton:pressed {
                background-color: %s;
            }
            QPushButton:disabled {
                background-color: %s;
            }
            """
            % (color, font_color, hover_color, pressed_color, disabled_color)
        )

    def setText(self, text: str):
        super().setText(f" {text}")
