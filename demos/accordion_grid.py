import sys
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor, QFont, QPixmap, QPainter, QFontMetrics
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QGroupBox,
    QSplitter
)

from qextrawidgets.widgets.grouped_icon_view.accordion_grid_view import AccordionGridView


# Importa suas classes refatoradas


def char_to_pixmap(char: str, color: QColor, size: int = 64) -> QPixmap:
    """
    Helper para criar ícones de teste baseados em texto.
    """
    font = QFont("Arial", int(size * 0.6))
    font.setBold(True)

    metrics = QFontMetrics(font)
    rect = metrics.boundingRect(char)

    # Cria pixmap quadrado
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    # Desenha um círculo de fundo
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(color)
    painter.drawEllipse(2, 2, size - 4, size - 4)

    # Desenha a letra centralizada
    painter.setPen(Qt.GlobalColor.white)
    painter.setFont(font)

    # Centralização manual
    x = (size - rect.width()) // 2 - rect.left()
    y = (size - metrics.ascent()) // 2 + metrics.ascent()

    painter.drawText(x, y, char)
    painter.end()

    return pixmap


class AccordionDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QExtraWidgets - Accordion Grid Demo")
        self.resize(1000, 700)

        # 1. Setup Main Widget & Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # 2. Setup Accordion View
        # Inicializa com valores padrão configuráveis no init
        self.view = AccordionGridView(
            icon_size=QSize(80, 80),
            margin=10,
            header_height=40
        )

        # 3. Setup Model
        self.model = QStandardItemModel()
        self._populate_model()
        self.view.setModel(self.model)

        # 4. Setup Controls (Sidebar)
        controls_panel = self._create_controls()

        # 5. Add to Layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.view)
        splitter.addWidget(controls_panel)
        splitter.setStretchFactor(0, 1)  # View expande mais

        main_layout.addWidget(splitter)

    def _populate_model(self):
        """Popula o modelo com Categorias e Itens de teste."""
        root = self.model.invisibleRootItem()

        # Configuração de dados de teste
        categories = [
            ("Applications", QColor("#3498db"), ["A", "B", "C", "D", "E"]),
            ("Media", QColor("#e74c3c"), ["M", "P", "3", "4", "V"]),
            ("Documents", QColor("#f1c40f"), ["D", "O", "C", "X", "T", "P"]),
            ("System", QColor("#9b59b6"), ["S", "Y", "R", "K"])
        ]

        for cat_name, color, items in categories:
            # Criar Categoria (Pai)
            cat_item = QStandardItem(cat_name)
            cat_item.setEditable(False)

            # Adicionar Filhos (Itens Grid)
            for char in items:
                child_item = QStandardItem(char)  # Texto (ignorado pelo delegate, mas útil debug)
                child_item.setEditable(False)

                # Gera ícone dinâmico
                icon_pixmap = char_to_pixmap(char, color)
                child_item.setData(icon_pixmap, Qt.ItemDataRole.DecorationRole)

                cat_item.appendRow(child_item)

            root.appendRow(cat_item)

            # Expande a primeira linha por padrão para visualização
            if cat_name == "Applications":
                # Precisamos fazer isso após o modelo ser anexado ou via lógica da view.
                # Como a view controla o estado expandido localmente (_expanded_rows),
                # vamos simular um clique ou acessar o set privado se necessário.
                # A view atual não tem método público 'expand', então o usuário clica.
                pass

    def _create_controls(self) -> QGroupBox:
        group = QGroupBox("Live Settings")
        group.setFixedWidth(250)
        layout = QVBoxLayout(group)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Slider: Icon Size ---
        lbl_size = QLabel(f"Icon Size: {self.view.iconSize().width()}px")
        slider_size = QSlider(Qt.Orientation.Horizontal)
        slider_size.setRange(40, 200)
        slider_size.setValue(self.view.iconSize().width())

        def update_size(val):
            self.view.setIconSize(QSize(val, val))
            lbl_size.setText(f"Icon Size: {val}px")

        slider_size.valueChanged.connect(update_size)

        layout.addWidget(lbl_size)
        layout.addWidget(slider_size)
        layout.addSpacing(20)

        # --- Slider: Margin ---
        lbl_margin = QLabel(f"Margin: {self.view.margin()}px")
        slider_margin = QSlider(Qt.Orientation.Horizontal)
        slider_margin.setRange(0, 50)
        slider_margin.setValue(self.view.margin())

        def update_margin(val):
            self.view.setMargin(val)
            lbl_margin.setText(f"Margin: {val}px")

        slider_margin.valueChanged.connect(update_margin)

        layout.addWidget(lbl_margin)
        layout.addWidget(slider_margin)
        layout.addSpacing(20)

        # --- Slider: Header Height ---
        lbl_header = QLabel(f"Header Height: {self.view.headerHeight()}px")
        slider_header = QSlider(Qt.Orientation.Horizontal)
        slider_header.setRange(20, 100)
        slider_header.setValue(self.view.headerHeight())

        def update_header(val):
            self.view.setHeaderHeight(val)
            lbl_header.setText(f"Header Height: {val}px")

        slider_header.valueChanged.connect(update_header)

        layout.addWidget(lbl_header)
        layout.addWidget(slider_header)

        # --- Instructions ---
        layout.addStretch()
        note = QLabel("Note:\nClick on Category Headers\nto expand/collapse.")
        note.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(note)

        return group


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Opcional: Ajuste de estilo para parecer moderno
    app.setStyle("Fusion")

    window = AccordionDemo()
    window.show()

    sys.exit(app.exec())