from PySide6.QtCore import QRunnable, QObject, Signal, QUrl, QUrlQuery
from PySide6.QtGui import QImage


class QImageProvider(QRunnable, QObject):
    success = Signal(QUrlQuery, QImage)
    error = Signal(QUrlQuery)

    def __init__(self, url_query: QUrlQuery):
        QRunnable.__init__(self)
        QObject.__init__(self)
        self._url_query = url_query