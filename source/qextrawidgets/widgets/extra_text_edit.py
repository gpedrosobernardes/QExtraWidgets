from PySide6.QtCore import QMimeData, QSize, Qt
from PySide6.QtWidgets import QTextEdit, QSizePolicy

# Ensure the import is correct for your project
from qextrawidgets.documents.twemoji_text_document import QTwemojiTextDocument


class QExtraTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Document Configuration
        self.setDocument(QTwemojiTextDocument(self))

        # Private Variables
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

    def createMimeDataFromSelection(self) -> QMimeData:
        """Preserves custom emojis when copying/dragging."""
        document: QTwemojiTextDocument = self.document()
        custom_text = document.toText(self.textCursor())

        new_mime_data = QMimeData()
        new_mime_data.setText(custom_text)
        return new_mime_data

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
