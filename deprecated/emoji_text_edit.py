from PySide6.QtCore import QMimeData
from PySide6.QtWidgets import QWidget

from qextrawidgets import QExtraTextEdit, QEmojiTextDocument


class QEmojiTextEdit(QExtraTextEdit):
    """A text edit widget that uses QTwemojiTextDocument to render emojis as images."""

    def __init__(self, parent: QWidget = None) -> None:
        """Initializes the twemoji text edit.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        document = QEmojiTextDocument()
        document.setDevicePixelRatio(self.devicePixelRatio())
        self.setDocument(document)

    def createMimeDataFromSelection(self) -> QMimeData:
        """Preserves custom emojis when copying or dragging.

        Returns:
            QMimeData: The generated MIME data.
        """
        document = self.document()
        custom_text = document.selectionToPlainText(self.textCursor())

        new_mime_data = QMimeData()
        new_mime_data.setText(custom_text)
        return new_mime_data

    def document(self) -> QEmojiTextDocument:
        """Returns the current twemoji text document.

        Returns:
            QEmojiTextDocument: The document.
        """
        return super().document()

    def setDocument(self, document: QEmojiTextDocument) -> None:
        """Sets the twemoji text document.

        Args:
            document (QEmojiTextDocument): The document to set.
        """
        super().setDocument(document)