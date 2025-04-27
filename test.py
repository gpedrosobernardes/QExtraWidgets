import sys
import qtawesome as qta
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableView, QWidget, QVBoxLayout
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

from extra_qwidgets.widgets.filterable_table.custom_header import CustomHeader


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Header com Ícone à Direita")
        self.resize(600, 400)

        self.table = QTableView(self)
        self.model = QStandardItemModel(5, 3, self)

        # Substitui o header padrão
        header = CustomHeader(Qt.Orientation.Horizontal, self.table)
        self.table.setHorizontalHeader(header)
        self.table.setModel(self.model)

        # Popula só o header com fa6b.github
        for col in range(3):
            item = QStandardItem(f"Coluna {col + 1}")
            item.setIcon(qta.icon('fa6b.github'))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # respeita esse alinhamento
            self.model.setHorizontalHeaderItem(col, item)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.table)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
