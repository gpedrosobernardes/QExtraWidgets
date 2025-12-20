from PySide6.QtCore import QMimeData
from PySide6.QtWidgets import QTextEdit

from extra_qwidgets.documents.twemoji_text_document import QTwemojiTextDocument


class QExtraTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocument(QTwemojiTextDocument(self))
        self._maximum_height = float('inf')
        self._responsive = False

        self.setResponsive(True)

    def createMimeDataFromSelection(self) -> QMimeData:
        document: QTwemojiTextDocument = self.document()
        custom_text = document.toText(self.textCursor())

        new_mime_data = QMimeData()
        new_mime_data.setText(custom_text)
        return new_mime_data

    def setResponsive(self, responsive=True):
        if self._responsive == responsive:
            return

        self._responsive = responsive

        size_policy = self.sizePolicy()
        size_policy.setVerticalStretch(int(responsive))
        self.setSizePolicy(size_policy)

        if responsive:
            self.textChanged.connect(self._adjust_height)
            self._adjust_height()
        else:
            try:
                self.textChanged.disconnect(self._adjust_height)
            except TypeError:
                # Evita erro se não estiver conectado
                pass
            self._maximum_height = float('inf')

    def responsive(self):
        return self._responsive

    def setMaximumHeight(self, height):
        if self.responsive():
            self._maximum_height = height
        else:
            super(QExtraTextEdit, self).setMaximumHeight(height)

    def maximumHeight(self):
        if self.responsive():
            return self._maximum_height
        else:
            return super(QExtraTextEdit, self).maximumHeight()

    def _adjust_height(self):
        content_margin = self.contentsMargins()
        document_height = self.document().size().height() + content_margin.top() + content_margin.bottom()
        height = min(document_height, self._maximum_height)

        if height == self._maximum_height:
            return

        if self.layout():
            size = self.size()
            size.setHeight(height)
            self.setMinimumSize(size)
            self.updateGeometry()
        else:
            self.setFixedHeight(height)