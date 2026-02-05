import sys

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QCheckBox, QSpinBox, QLabel, QPushButton, QGroupBox, QFormLayout
)

from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.gui.validators import QEmojiValidator
from qextrawidgets.widgets.inputs.twemoji_text_edit import QEmojiTextEdit


class DemoTextEditWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QExtraTextEdit Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))
        self.resize(500, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        self._main_layout = QVBoxLayout(central_widget)
        self._main_layout.setSpacing(15)

        # Components
        self._text_edit = None
        self._chk_responsive = None
        self._chk_twemoji = None
        self._chk_aliases = None
        self._chk_validator = None
        self._spin_max_height = None
        self._spin_emoji_margin = None
        self._spin_font_size = None
        self._lbl_status = None
        self._emoji_validator = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        # 1. Instructions Header
        lbl_intro = QLabel(
            "<h3>Test Instructions:</h3>"
            "<ul>"
            "<li>Type <b>:smile:</b>, <b>:rocket:</b> or <b>:heart:</b> to test aliases.</li>"
            "<li>Paste a real emoji (e.g., 🔥, 😂) to test Unicode replacement.</li>"
            "<li>Type multiple lines to see the field grow (Responsiveness).</li>"
            "<li>Enable the <b>Validator</b> to restrict input to emojis only.</li>"
            "</ul>"
        )
        lbl_intro.setWordWrap(True)
        self._main_layout.addWidget(lbl_intro)

        # 2. The Main Widget (QExtraTextEdit)
        self._text_edit = QEmojiTextEdit()
        self._text_edit.setPlaceholderText("Type here... Try :100: or paste an emoji.")

        # Define an initial maximum height to demonstrate scrolling
        self._text_edit.setMaximumHeight(150)

        self._main_layout.addWidget(self._text_edit)

        # 3. Control Panel (To test APIs)
        group_controls = QGroupBox("Real-Time Settings")
        layout_controls = QFormLayout(group_controls)

        # Toggle: Responsiveness (Auto-grow)
        self._chk_responsive = QCheckBox("Enable Responsiveness (Auto-Height)")
        self._chk_responsive.setChecked(self._text_edit.isResponsive())

        # Control: Maximum Height
        self._spin_max_height = QSpinBox()
        self._spin_max_height.setRange(50, 1000)
        self._spin_max_height.setValue(self._text_edit.maximumHeight())
        self._spin_max_height.setSuffix(" px")

        # Toggle: Twemoji Rendering
        self._chk_twemoji = QCheckBox("Enable Twemoji (Images)")
        # Access the custom document
        self._chk_twemoji.setChecked(self._text_edit.document().twemoji())

        # Toggle: Alias Replacement (:smile:)
        self._chk_aliases = QCheckBox("Replace Aliases (e.g., :smile:)")
        self._chk_aliases.setChecked(self._text_edit.document().aliasReplacement())

        # Toggle: Emoji Validator
        self._chk_validator = QCheckBox("Enable Emoji Validator (Emojis Only)")
        self._chk_validator.setChecked(False)

        # Control: Emoji Margin
        self._spin_emoji_margin = QSpinBox()
        self._spin_emoji_margin.setRange(0, 50)
        self._spin_emoji_margin.setValue(self._text_edit.document().emojiMargin())
        self._spin_emoji_margin.setSuffix(" px")

        # Control: Font Size
        self._spin_font_size = QSpinBox()
        self._spin_font_size.setRange(8, 72)
        self._spin_font_size.setValue(int(self._text_edit.font().pointSize()))
        self._spin_font_size.setSuffix(" pt")

        layout_controls.addRow(self._chk_responsive)
        layout_controls.addRow("Maximum Height:", self._spin_max_height)
        layout_controls.addRow(self._chk_twemoji)
        layout_controls.addRow(self._chk_aliases)
        layout_controls.addRow(self._chk_validator)
        layout_controls.addRow("Emoji Margin:", self._spin_emoji_margin)
        layout_controls.addRow("Font Size:", self._spin_font_size)

        self._main_layout.addWidget(group_controls)

        # 4. Debug Button
        btn_debug = QPushButton("Print Content to Console")
        btn_debug.clicked.connect(self._print_debug_info)
        self._main_layout.addWidget(btn_debug)

        # Spacer to push everything up
        self._main_layout.addStretch()

    def _connect_signals(self):
        # Connect controls to public widget methods
        self._chk_responsive.toggled.connect(self._text_edit.setResponsive)
        self._spin_max_height.valueChanged.connect(self._text_edit.setMaximumHeight)

        # Connect document settings
        # Note: QExtraTextEdit uses QTwemojiTextDocument internally
        doc = self._text_edit.document()
        self._chk_twemoji.toggled.connect(doc.setTwemoji)
        self._chk_aliases.toggled.connect(doc.setAliasReplacement)
        self._spin_emoji_margin.valueChanged.connect(doc.setEmojiMargin)

        # Connect validator
        self._chk_validator.toggled.connect(self._toggle_validator)

        # Connect font size change
        self._spin_font_size.valueChanged.connect(self._change_font_size)

    def _toggle_validator(self, checked: bool):
        if checked:
            if not self._emoji_validator:
                self._emoji_validator = QEmojiValidator(self)
            self._text_edit.setValidator(self._emoji_validator)
            self._text_edit.setPlaceholderText("Only emojis allowed! (e.g. 🚀)")
        else:
            self._text_edit.setValidator(None)
            self._text_edit.setPlaceholderText("Type here... Try :100: or paste an emoji.")

    def _change_font_size(self, size):
        document = self._text_edit.document()
        font = document.defaultFont()
        font.setPointSize(size)
        document.setDefaultFont(font)

    def _print_debug_info(self):
        print("-" * 40)
        print("DEBUG INFO:")
        print(f"Plain Text (.toPlainText): {self._text_edit.toPlainText()}")
        # To see how images are handled internally by Qt
        print(f"Qt HTML (.toHtml): {self._text_edit.toHtml()[:200]}...")
        print(f"Current Height: {self._text_edit.height()}")
        print("-" * 40)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # We do not use Fusion style as requested in saved rules.

    window = DemoTextEditWindow()
    window.show()

    sys.exit(app.exec())
