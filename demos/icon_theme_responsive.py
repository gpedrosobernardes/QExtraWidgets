import sys

import qtawesome
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QGuiApplication
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QToolButton, QFrame, QGroupBox
)

from extra_qwidgets.icons import QThemeResponsiveIcon
from extra_qwidgets.utils import is_dark_mode


class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo QAutoIcon e Temas")
        self.resize(600, 500)

        # --- Configuração da UI ---
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # 1. Seção de Controle do Tema
        btn_theme_toggle = QPushButton("Alternar Tema (Claro / Escuro)")
        btn_theme_toggle.setFixedHeight(40)
        btn_theme_toggle.setIconSize(QSize(32, 32))
        # Um ícone simples para o botão de tema
        btn_theme_toggle.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.palette"))
        btn_theme_toggle.clicked.connect(self.toggleTheme)

        main_layout.addWidget(btn_theme_toggle)

        # Separador visual
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        # 2. Seção de Ícones Padrão (QtAwesome direto)
        group_standard = QGroupBox("Ícones Padrão (QtAwesome -> QAutoIcon)")
        layout_standard = QHBoxLayout()

        # Botão Normal
        btn_rocket = QPushButton("Botão Normal")
        btn_rocket.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.rocket"))
        btn_rocket.setIconSize(QSize(32, 32))

        # ToolButton (Flat)
        btn_gear = QToolButton()
        btn_gear.setText("ToolButton Flat")
        btn_gear.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.gear"))
        btn_gear.setIconSize(QSize(32, 32))
        btn_gear.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        btn_gear.setAutoRaise(True)

        # Botão Desabilitado (Teste importante para ver a cor de 'Disabled')
        btn_disabled = QPushButton("Desabilitado")
        btn_disabled.setIcon(QThemeResponsiveIcon.fromAwesome("fa6s.ban"))
        btn_disabled.setIconSize(QSize(32, 32))
        btn_disabled.setEnabled(False)

        layout_standard.addWidget(btn_rocket)
        layout_standard.addWidget(btn_gear)
        layout_standard.addWidget(btn_disabled)
        group_standard.setLayout(layout_standard)
        main_layout.addWidget(group_standard)

        # 3. Seção de Teste de Múltiplos Pixmaps (Estados)
        group_multistate = QGroupBox("Ícone com Múltiplos Estados (On/Off)")
        layout_multistate = QVBoxLayout()

        lbl_info = QLabel("Este botão muda de ícone quando clicado (Checked/Unchecked).\n"
                          "Ambos os ícones (vazio e marcado) devem seguir a cor do tema.")
        lbl_info.setStyleSheet("color: gray; font-style: italic; margin-bottom: 10px;")

        # --- CRIAÇÃO DO ÍCONE MULTI-ESTADO ---
        # Passo A: Criar um QIcon base normal
        base_multi_icon = QIcon()

        # Passo B: Gerar pixmaps para os estados usando qtawesome
        # Nota: Usamos cor 'black' neutra, pois o QAutoIcon vai sobrescrever a cor.

        # Estado OFF (Normal, Off): Quadrado vazio ("fa6r.square" - regular style)
        pix_off = qtawesome.icon("fa6s.square", color="black").pixmap(QSize(48, 48))
        base_multi_icon.addPixmap(pix_off, QIcon.Mode.Normal, QIcon.State.Off)

        # Estado ON (Normal, On): Quadrado marcado ("fa6s.square-check" - solid style)
        pix_on = qtawesome.icon("fa6s.square-check", color="black").pixmap(QSize(48, 48))
        base_multi_icon.addPixmap(pix_on, QIcon.Mode.Normal, QIcon.State.On)

        # Passo C: Envolver o ícone base no nosso QAutoIcon
        # O motor agora sabe lidar com os múltiplos estados internos
        auto_multi_icon = QThemeResponsiveIcon(base_multi_icon)

        # Passo D: Criar o botão que usa esse ícone
        self.btn_toggle_state = QPushButton("Clique para Alternar Estado")
        self.btn_toggle_state.setFixedHeight(50)
        self.btn_toggle_state.setCheckable(True)  # Importante!
        self.btn_toggle_state.setIcon(auto_multi_icon)
        self.btn_toggle_state.setIconSize(QSize(48, 48))

        # Conexão apenas para mudar o texto para feedback visual
        self.btn_toggle_state.toggled.connect(self.updateToggleBtnText)

        layout_multistate.addWidget(lbl_info)
        layout_multistate.addWidget(self.btn_toggle_state)
        group_multistate.setLayout(layout_multistate)
        main_layout.addWidget(group_multistate)

        # Inicializa com o tema claro
        self.applyLightTheme()

    def updateToggleBtnText(self, checked):
        state_text = "MARCADO (ON)" if checked else "DESMARCADO (OFF)"
        self.btn_toggle_state.setText(f"Clique para Alternar Estado - {state_text}")

    def toggleTheme(self):
        """Alterna entre as paletas e aplica na aplicação inteira."""
        if is_dark_mode():
            self.applyLightTheme()
        else:
            self.applyDarkTheme()

    def applyDarkTheme(self):
        """Aplica uma paleta escura genérica."""
        QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Dark)

    def applyLightTheme(self):
        """Restaura a paleta padrão do sistema (Clara)."""
        # Usar a paleta padrão do estilo Fusion geralmente é uma paleta clara limpa
        QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = DemoWindow()
    window.show()
    sys.exit(app.exec())