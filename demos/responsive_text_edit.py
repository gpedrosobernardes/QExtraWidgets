from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication

from extra_qwidgets.icons import QThemeResponsiveIcon
from extra_qwidgets.widgets.extra_text_edit import QExtraTextEdit


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QExtraTextEdit Example")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        self.text_edit = QExtraTextEdit()
        self.text_edit.setMaximumHeight(250)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()