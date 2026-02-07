import typing
import sys
from PySide6.QtCore import QTimer

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QCheckBox,
    QSpinBox,
    QLabel,
    QPushButton,
    QGroupBox,
    QFormLayout,
)

from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.gui.validators import QEmojiValidator
from qextrawidgets.widgets.inputs.extra_text_edit import QExtraTextEdit


LOREM_IPSUM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut "
    "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
    "laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in "
    "voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat "
    "non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n\n"
    "Curabitur pretium tincidunt lacus. Nulla gravida orci a odio. Nullam varius, turpis et commodo "
    "pharetra, est eros bibendum elit, nec luctus magna felis sollicitudin mauris. Integer in mauris "
    "eu nibh euismod gravida. Duis ac tellus et risus vulputate vehicula. Donec lobortis risus a elit. "
    "Etiam tempor. Ut ullamcorper, ligula eu tempor congue, eros est euismod turpis, id tincidunt "
    "sapien risus a quam. Maecenas fermentum consequat mi. Donec fermentum. Pellentesque malesuada "
    "nulla a mi. Duis sapien sem, aliquet nec, commodo eget, consequat quis, neque. Aliquam faucibus, "
    "elit ut dictum aliquet, felis nisl adipiscing sapien, sed malesuada diam lacus eget erat. Cras "
    "mollis scelerisque nunc. Nullam arcu. Aliquam consequat. Curabitur augue lorem, dapibus quis, "
    "laoreet et, pretium ac, nisi. Aenean magna nisl, mollis quis, molestie eu, feugiat in, orci. "
    "In hac habitasse platea dictumst."
)


class DemoTextEditWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QExtraTextEdit Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))
        self.resize(500, 400)

        self._emoji_validator = QEmojiValidator()

        self._timer_fill = QTimer(self)
        self._timer_fill.setInterval(10)  # 10ms per character
        self._timer_fill.timeout.connect(self._on_fill_tick)
        self._fill_iterator: typing.Optional[typing.Iterator[str]] = None

        self._init_widgets()
        self.setup_layout()
        self.setup_connections()

    def _init_widgets(self) -> None:
        # 1. Instructions Header
        self.lbl_intro = QLabel(
            "<h3>Test Instructions:</h3>"
            "<ul>"
            "<li>Type multiple lines to see the field grow (Responsiveness).</li>"
            "<li>Enable the <b>Validator</b> to restrict input to emojis only.</li>"
            "</ul>"
        )
        self.lbl_intro.setWordWrap(True)

        # 2. The Main Widget (QExtraTextEdit)
        self._text_edit = QExtraTextEdit()
        self._text_edit.setPlaceholderText("Type here... Try :100: or paste an emoji.")
        # Define an initial maximum height to demonstrate scrolling
        self._text_edit.setMaximumHeight(200)

        # 3. Control Panel (To test APIs)
        self.group_controls = QGroupBox("Real-Time Settings")

        # Toggle: Responsiveness (Auto-grow)
        self._chk_responsive = QCheckBox("Enable Responsiveness (Auto-Height)")
        self._chk_responsive.setChecked(self._text_edit.isResponsive())

        # Control: Maximum Height
        self._spin_max_height = QSpinBox()
        self._spin_max_height.setRange(50, 1000)
        self._spin_max_height.setValue(self._text_edit.maximumHeight())
        self._spin_max_height.setSuffix(" px")

        # Toggle: Emoji Validator
        self._chk_validator = QCheckBox("Enable Emoji Validator (Emojis Only)")
        self._chk_validator.setChecked(False)

        # Button: Async Fill
        self._btn_fill = QPushButton("Fill with Lorem Ipsum")

    def setup_layout(self) -> None:
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)

        main_layout.addWidget(self.lbl_intro)
        main_layout.addWidget(self._text_edit)

        layout_controls = QFormLayout(self.group_controls)
        layout_controls.addRow(self._chk_responsive)
        layout_controls.addRow("Maximum Height:", self._spin_max_height)
        layout_controls.addRow(self._chk_validator)
        layout_controls.addRow(self._btn_fill)

        main_layout.addWidget(self.group_controls)

        # Spacer to push everything up
        main_layout.addStretch()

    def setup_connections(self) -> None:
        # Connect controls to public widget methods
        self._chk_responsive.toggled.connect(self._text_edit.setResponsive)
        self._spin_max_height.valueChanged.connect(self._text_edit.setMaximumHeight)
        self._btn_fill.clicked.connect(self._start_async_fill)

        # Connect validator
        self._chk_validator.toggled.connect(self._toggle_validator)

    def _toggle_validator(self, checked: bool):
        if checked:
            self._text_edit.setValidator(self._emoji_validator)
            self._text_edit.setPlaceholderText("Only emojis allowed! (e.g. 🚀)")
        else:
            self._text_edit.setValidator(None)
            self._text_edit.setPlaceholderText("Type here... or paste an emoji.")

    def _change_font_size(self, size):
        document = self._text_edit.document()
        font = document.defaultFont()
        font.setPointSize(size)
        document.setDefaultFont(font)

    def _start_async_fill(self):
        """Starts filling the text edit with Lorem Ipsum gradually."""
        self._text_edit.clear()
        self._fill_iterator = iter(LOREM_IPSUM)
        # Reset and start the timer
        self._timer_fill.start()
        # Disable button while running to prevent double clicks
        self._btn_fill.setEnabled(False)

    def _on_fill_tick(self):
        """Called by timer to add one character."""
        if self._fill_iterator is None:
            self._timer_fill.stop()
            return

        try:
            char = next(self._fill_iterator)
            self._text_edit.insertPlainText(char)
            # Optional: Scroll to end to follow the text
            self._text_edit.ensureCursorVisible()
        except StopIteration:
            self._timer_fill.stop()
            self._btn_fill.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # We do not use Fusion style as requested in saved rules.

    window = DemoTextEditWindow()
    window.show()

    sys.exit(app.exec())
