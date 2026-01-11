from PySide6.QtCore import QMimeData, QSize, Qt
from PySide6.QtGui import QKeyEvent, QValidator
from PySide6.QtWidgets import QTextEdit, QSizePolicy

# Ensure the import is correct for your project
from qextrawidgets.documents.twemoji_text_document import QTwemojiTextDocument


class QExtraTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Private Variables
        self._validator = None
        self._max_height = 16777215  # QWIDGETSIZE_MAX (Qt Default)
        self._responsive = False

        # Initialization
        self.setResponsive(True)

        # Size Policy Adjustment
        # For a growing widget, 'Minimum' or 'Preferred' vertically is better than 'Expanding'
        size_policy = self.sizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Policy.Minimum)
        self.setSizePolicy(size_policy)

    # --- Qt System Overrides ---

    def sizeHint(self) -> QSize:
        """
        Informs the layout of the ideal size of the widget at this moment.
        """
        if self._responsive and self.document():
            # 1. Calculates the height of the actual content
            doc_height = self.document().size().height()

            # 2. Adds internal margins and frame borders
            # frameWidth() covers borders drawn by the style
            margins = self.contentsMargins()
            frame_borders = self.frameWidth() * 2

            total_height = doc_height + margins.top() + margins.bottom() + frame_borders

            # 3. Limits to the defined maximum height
            final_height = min(total_height, self._max_height)

            return QSize(super().sizeHint().width(), int(final_height))

        return super().sizeHint()

    # --- Getters and Setters ---

    def responsive(self) -> bool:
        return self._responsive

    def setResponsive(self, responsive: bool = True):
        if self._responsive == responsive:
            return

        self._responsive = responsive

        if responsive:
            self.textChanged.connect(self._on_text_changed)
            # Removes default automatic scroll policy to manage manually
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self._on_text_changed()  # Forces initial adjustment
        else:
            try:
                self.textChanged.disconnect(self._on_text_changed)
            except RuntimeError:
                pass

            # Restores default behavior
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.updateGeometry()

    def maximumHeight(self) -> int:
        return self._max_height

    def setMaximumHeight(self, height: int):
        self._max_height = height
        # We don't call super().setMaximumHeight here to not lock the widget visually
        # The constraint is applied logically in sizeHint
        self.updateGeometry()

    def setValidator(self, validator: QValidator):
        self._validator = validator

    def validator(self) -> QValidator:
        return self._validator

    # --- Internal Logic ---

    def _on_text_changed(self):
        """Called when text changes to recalculate geometry."""
        if not self._responsive:
            return

        # 1. Notifies layout that ideal size changed
        self.updateGeometry()

        # 2. Manages ScrollBar visibility
        # If content is larger than max limit, we need scrollbar
        doc_height = self.document().size().height()
        content_margins = self.contentsMargins().top() + self.contentsMargins().bottom() + (self.frameWidth() * 2)

        if (doc_height + content_margins) > self._max_height:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def keyPressEvent(self, event: QKeyEvent):
        if self._validator is None:
            return super().keyPressEvent(event)

        # Step A: Allow control keys (Backspace, Delete, Enter, Arrows, Tab, Ctrl+C, etc.)
        # If not done, the editor becomes unusable (cannot delete or navigate).
        is_control = (
                event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete, Qt.Key.Key_Return,
                                Qt.Key.Key_Enter, Qt.Key.Key_Tab, Qt.Key.Key_Left, Qt.Key.Key_Right,
                                Qt.Key.Key_Up, Qt.Key.Key_Down) or
                event.modifiers() & Qt.KeyboardModifier.ControlModifier  # Allows shortcuts like Ctrl+C
        )

        if is_control:
            return super().keyPressEvent(event)

        text = event.text()

        state, _, _ = self._validator.validate(text, 0)

        if state == QValidator.State.Acceptable:
            super().keyPressEvent(event)
        return None

    def insertFromMimeData(self, source: QMimeData):
        if source.hasText() and self._validator is not None:
            state, _, _ = self._validator.validate(source.text(), 0)
            if state == QValidator.State.Acceptable:
                super().insertFromMimeData(source)
        else:
            super().insertFromMimeData(source)