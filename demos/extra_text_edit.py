import sys

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QCheckBox, QSpinBox, QLabel, QPushButton, QGroupBox, QFormLayout
)

from extra_qwidgets.widgets.extra_text_edit import QExtraTextEdit


class DemoTextEditWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo: TextEdit Responsivo + Twemoji")
        self.resize(500, 600)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        self._main_layout = QVBoxLayout(central_widget)
        self._main_layout.setSpacing(15)

        # Componentes
        self._text_edit = None
        self._chk_responsive = None
        self._chk_twemoji = None
        self._chk_aliases = None
        self._spin_max_height = None
        self._lbl_status = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        # 1. Cabeçalho de Instruções
        lbl_intro = QLabel(
            "<h3>Instruções de Teste:</h3>"
            "<ul>"
            "<li>Digite <b>:smile:</b>, <b>:rocket:</b> ou <b>:heart:</b> para testar aliases.</li>"
            "<li>Cole um emoji real (ex: 🔥, 😂) para testar a substituição Unicode.</li>"
            "<li>Digite várias linhas para ver o campo crescer (Responsividade).</li>"
            "</ul>"
        )
        lbl_intro.setWordWrap(True)
        self._main_layout.addWidget(lbl_intro)

        # 2. O Widget Principal (QExtraTextEdit)
        self._text_edit = QExtraTextEdit()
        self._text_edit.setPlaceholderText("Digite aqui... Tente :100: ou cole um emoji.")
        # Define uma altura inicial máxima para demonstrar o scroll
        self._text_edit.setMaximumHeight(150)

        self._main_layout.addWidget(self._text_edit)

        # 3. Painel de Controle (Para testar as APIs)
        group_controls = QGroupBox("Configurações em Tempo Real")
        layout_controls = QFormLayout(group_controls)

        # Toggle: Responsividade (Auto-grow)
        self._chk_responsive = QCheckBox("Ativar Responsividade (Auto-Height)")
        self._chk_responsive.setChecked(self._text_edit.responsive())

        # Controle: Altura Máxima
        self._spin_max_height = QSpinBox()
        self._spin_max_height.setRange(50, 1000)
        self._spin_max_height.setValue(self._text_edit.maximumHeight())
        self._spin_max_height.setSuffix(" px")

        # Toggle: Renderização de Twemoji
        self._chk_twemoji = QCheckBox("Ativar Twemoji (Imagens)")
        # Acessa o documento customizado
        self._chk_twemoji.setChecked(self._text_edit.document().twemoji())

        # Toggle: Substituição de Alias (:smile:)
        self._chk_aliases = QCheckBox("Substituir Aliases (ex: :smile:)")
        self._chk_aliases.setChecked(self._text_edit.document().aliasReplacement())

        layout_controls.addRow(self._chk_responsive)
        layout_controls.addRow("Altura Máxima:", self._spin_max_height)
        layout_controls.addRow(self._chk_twemoji)
        layout_controls.addRow(self._chk_aliases)

        self._main_layout.addWidget(group_controls)

        # 4. Botão de Debug
        btn_debug = QPushButton("Imprimir Conteúdo no Console")
        btn_debug.clicked.connect(self._print_debug_info)
        self._main_layout.addWidget(btn_debug)

        # Espaçador para empurrar tudo para cima
        self._main_layout.addStretch()

    def _connect_signals(self):
        # Conecta os controles aos métodos públicos do widget
        self._chk_responsive.toggled.connect(self._text_edit.setResponsive)
        self._spin_max_height.valueChanged.connect(self._text_edit.setMaximumHeight)

        # Conecta configurações do documento
        # Nota: QExtraTextEdit usa QTwemojiTextDocument internamente
        doc = self._text_edit.document()
        self._chk_twemoji.toggled.connect(doc.setTwemoji)
        self._chk_aliases.toggled.connect(doc.setAliasReplacement)

    def _print_debug_info(self):
        print("-" * 40)
        print("DEBUG INFO:")
        print(f"Texto Puro (.toPlainText): {self._text_edit.toPlainText()}")
        # Para ver como as imagens são tratadas internamente pelo Qt
        print(f"HTML Qt (.toHtml): {self._text_edit.toHtml()[:200]}...")
        print(f"Altura Atual: {self._text_edit.height()}")
        print("-" * 40)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Não utilizamos estilo Fusion conforme solicitado nas regras salvas.

    window = DemoTextEditWindow()
    window.show()

    sys.exit(app.exec())