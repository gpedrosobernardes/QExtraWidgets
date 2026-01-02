import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QLabel, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QGroupBox, QRadioButton,
    QCheckBox, QLineEdit, QFormLayout, QTextEdit, QButtonGroup
)

from extra_qwidgets.icons import QThemeResponsiveIcon
from extra_qwidgets.widgets.accordion_item import QAccordionHeader
from source.extra_qwidgets.widgets.accordion import QAccordion


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Accordion Full Demo")
        self.resize(900, 700)

        # Tenta carregar ícone, fallback se não tiver o utilitário configurado
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        # Widget Principal
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # --- 1. Criação do Accordion ---
        self.accordion = QAccordion()
        self.populate_accordion()

        # --- 2. Painel de Controle (Lado Esquerdo) ---
        control_panel = self.create_control_panel()

        # Adiciona ao layout: Controles na esquerda (1/3), Accordion na direita (2/3)
        main_layout.addWidget(control_panel, 1)
        main_layout.addWidget(self.accordion, 2)

        self.setCentralWidget(main_widget)

    def create_control_panel(self) -> QWidget:
        """Cria um painel lateral para testar as funções públicas do Accordion."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Grupo: Visibilidade ---
        grp_vis = QGroupBox("Visibilidade Global")
        v_layout = QVBoxLayout()

        btn_expand = QPushButton("Expandir Tudo (expandAll)")
        btn_expand.clicked.connect(self.accordion.expandAll)

        btn_collapse = QPushButton("Recolher Tudo (collapseAll)")
        btn_collapse.clicked.connect(self.accordion.collapseAll)

        v_layout.addWidget(btn_expand)
        v_layout.addWidget(btn_collapse)
        grp_vis.setLayout(v_layout)
        layout.addWidget(grp_vis)

        # --- Grupo: Estilo do Ícone ---
        grp_style = QGroupBox("Estilo do Ícone (setIconStyle)")
        v_style = QVBoxLayout()
        bg_style = QButtonGroup(self)

        rb_arrow = QRadioButton("Arrow (Seta)")
        rb_arrow.setChecked(True)
        rb_arrow.toggled.connect(lambda: self.accordion.setIconStyle(QAccordionHeader.IndicatorStyle.Arrow))

        rb_plus = QRadioButton("Plus / Minus (+/-)")
        rb_plus.toggled.connect(lambda: self.accordion.setIconStyle(QAccordionHeader.IndicatorStyle.PlusMinus))

        bg_style.addButton(rb_arrow)
        bg_style.addButton(rb_plus)
        v_style.addWidget(rb_arrow)
        v_style.addWidget(rb_plus)
        grp_style.setLayout(v_style)
        layout.addWidget(grp_style)

        # --- Grupo: Posição do Ícone ---
        grp_pos = QGroupBox("Posição do Ícone (setIconPosition)")
        v_pos = QVBoxLayout()
        bg_pos = QButtonGroup(self)

        rb_left = QRadioButton("Esquerda (Left)")
        rb_left.setChecked(True)
        rb_left.toggled.connect(lambda: self.accordion.setIconPosition(QAccordionHeader.IconPosition.LeadingPosition))

        rb_right = QRadioButton("Direita (Right)")
        rb_right.toggled.connect(lambda: self.accordion.setIconPosition(QAccordionHeader.IconPosition.TrailingPosition))

        bg_pos.addButton(rb_left)
        bg_pos.addButton(rb_right)
        v_pos.addWidget(rb_left)
        v_pos.addWidget(rb_right)
        grp_pos.setLayout(v_pos)
        layout.addWidget(grp_pos)

        # --- Grupo: Aparência ---
        grp_look = QGroupBox("Aparência")
        v_look = QVBoxLayout()

        chk_flat = QCheckBox("Flat Mode (setFlat)")
        chk_flat.toggled.connect(self.accordion.setFlat)

        v_look.addWidget(chk_flat)
        grp_look.setLayout(v_look)
        layout.addWidget(grp_look)

        # --- Grupo: Scroll ---
        grp_scroll = QGroupBox("Teste de Scroll")
        v_scroll = QVBoxLayout()

        btn_scroll_top = QPushButton("Reset Scroll (Topo)")
        btn_scroll_top.clicked.connect(self.accordion.resetScroll)

        # Vamos rolar até o item 4 (texto longo)
        btn_scroll_item = QPushButton("Scroll p/ Item Longo")
        btn_scroll_item.clicked.connect(
            lambda: self.accordion.scrollToItem(self.item_long_text)
        )

        # Vamos rolar apenas até o Header do Item 5
        btn_scroll_header = QPushButton("Scroll p/ Header Form")
        btn_scroll_header.clicked.connect(
            lambda: self.accordion.scrollToHeader(self.item_form)
        )

        v_scroll.addWidget(btn_scroll_top)
        v_scroll.addWidget(btn_scroll_item)
        v_scroll.addWidget(btn_scroll_header)
        grp_scroll.setLayout(v_scroll)
        layout.addWidget(grp_scroll)

        return panel

    def populate_accordion(self):
        """Adiciona seções variadas para demonstrar versatilidade."""

        # 1. Widget Simples
        self.accordion.addSection("1. Introdução", QLabel(
            "Este é um Accordion dinâmico em PySide6.\nUse o painel à esquerda para testar."))

        # 2. Configuração Individual (Override)
        # Este item não deve obedecer aos botões globais se configurarmos manualmente depois?
        # Nota: O método setIconPosition global itera sobre todos.
        # Aqui apenas mostramos que podemos adicionar e configurar na hora.
        lbl_custom = QLabel(
            "Este item foi adicionado e configurado individualmente\ncom ícone na direita inicialmente.")
        item_custom = self.accordion.addSection("2. Item Configurado Manualmente", lbl_custom)
        item_custom.setIconPosition("right")

        # 3. Layout Aninhado (Botões e ações)
        widget_actions = QWidget()
        layout_actions = QHBoxLayout(widget_actions)
        layout_actions.addWidget(QPushButton("Ação 1"))
        layout_actions.addWidget(QPushButton("Ação 2"))
        layout_actions.addWidget(QPushButton("Ação 3"))
        self.accordion.addSection("3. Container de Botões", widget_actions)

        # 4. Texto Longo (Para testar Scroll)
        long_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n" * 20
        txt_edit = QTextEdit()
        txt_edit.setPlainText(long_text)
        txt_edit.setMinimumHeight(200)  # Forçar altura para testar scroll do accordion
        self.item_long_text = self.accordion.addSection("4. Conteúdo Longo (Scroll Test)", txt_edit)

        # 5. Formulário Complexo
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.addRow("Nome:", QLineEdit())
        form_layout.addRow("Email:", QLineEdit())
        form_layout.addRow("Aceita Termos:", QCheckBox())
        self.item_form = self.accordion.addSection("5. Formulário de Cadastro", form_widget)

        # 6. Mais itens para encher espaço
        for i in range(6, 10):
            self.accordion.addSection(f"{i}. Item Extra", QLabel(f"Conteúdo do item {i}"))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())