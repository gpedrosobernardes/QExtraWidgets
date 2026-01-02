import sys
import random
from datetime import datetime, timedelta

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QHBoxLayout, QHeaderView
)

from extra_qwidgets.widgets.filterable_table.filterable_table import QFilterableTable


class DemoTableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo: QFilterableTable & FilterPopup")
        self.resize(800, 600)

        # Widget Central
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 1. Cabeçalho / Instruções
        header_layout = QHBoxLayout()
        lbl_instr = QLabel(
            "<h3>Instruções:</h3>"
            "<ul>"
            "<li>Clique no <b>ícone de filtro</b> (cabeçalho) para abrir o Popup.</li>"
            "<li>Teste o <b>Select All</b> e a <b>Busca</b>.</li>"
            "<li>Verifique se a lista do popup está ordenada alfabeticamente.</li>"
            "</ul>"
        )
        lbl_instr.setWordWrap(True)
        header_layout.addWidget(lbl_instr)

        layout.addLayout(header_layout)

        # 2. A Tabela Filtrável
        self.table = QFilterableTable()
        self.table.setAlternatingRowColors(True)

        # Estilo para melhor visualização (Colunas preenchem o espaço)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

        # 3. Popular Dados
        self.populate_data()

    def populate_data(self):
        """Cria um modelo com dados fictícios para teste."""
        model = QStandardItemModel()

        # Colunas
        headers = ["ID", "Nome", "Departamento", "Status", "Data", "Prioridade"]
        model.setHorizontalHeaderLabels(headers)

        # Dados Dummy
        departments = ["TI", "RH", "Financeiro", "Vendas", "Logística"]
        names = ["Ana", "Bruno", "Carlos", "Daniela", "Eduardo", "Fernanda", "Gabriel", "Helena"]
        statuses = ["Ativo", "Inativo", "Pendente", "Férias"]
        priorities = ["Alta", "Média", "Baixa"]

        # Gerar 100 linhas
        for i in range(1, 101):
            row_items = []

            # ID
            it_id = QStandardItem()
            it_id.setData(i, Qt.ItemDataRole.DisplayRole)
            row_items.append(it_id)

            # Nome
            name = f"{random.choice(names)} {random.choice(['Silva', 'Santos', 'Oliveira', 'Souza'])}"
            row_items.append(QStandardItem(name))

            # Departamento
            row_items.append(QStandardItem(random.choice(departments)))

            # Status
            status = random.choice(statuses)
            it_status = QStandardItem(status)

            # Exemplo de formatação condicional simples
            if status == "Ativo":
                it_status.setForeground(QColor("green"))
            elif status == "Inativo":
                it_status.setForeground(QColor("red"))

            row_items.append(it_status)

            # Data
            date = datetime.now() - timedelta(days=random.randint(0, 365))
            row_items.append(QStandardItem(date.strftime("%Y-%m-%d")))

            # Prioridade
            row_items.append(QStandardItem(random.choice(priorities)))

            model.appendRow(row_items)

        # Injeta o modelo na tabela
        self.table.setModel(model)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemoTableWindow()
    window.show()
    sys.exit(app.exec())