from PySide6.QtCore import QMimeData

from qextrawidgets import QExtraTextEdit, QTwemojiTextDocument


class QTwemojiTextEdit(QExtraTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocument(QTwemojiTextDocument())

    def createMimeDataFromSelection(self) -> QMimeData:
        """Preserves custom emojis when copying/dragging."""
        document: QTwemojiTextDocument = self.document()
        custom_text = document.selectionToPlainText(self.textCursor())

        new_mime_data = QMimeData()
        new_mime_data.setText(custom_text)
        return new_mime_data

    def document(self) -> QTwemojiTextDocument:
        return super().document()  # type: ignore

    def setDocument(self, document: QTwemojiTextDocument, /):
        return super().setDocument(document)