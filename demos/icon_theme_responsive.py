import sys
import qtawesome
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget # Importando a classe acima

from extra_qwidgets.icons import QThemeResponsiveIcon


class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 200)
        self.setWindowTitle("QAutoIcon com QtAwesome")

        layout = QVBoxLayout(self)

        # 1. Criando o ícone base do qtawesome
        # Nota: A cor aqui não importa muito, pois o QAutoIcon vai sobrescrever,
        # mas usar preto ou branco ajuda na depuração.

        # 2. Envolvendo no nosso QAutoIcon
        # Isso torna o ícone "vivo" para mudanças de tema
        auto_icon = QThemeResponsiveIcon.fromAwesome("fa6s.face-smile", color="black")

        # 3. Aplicando no botão
        btn = QPushButton("Botão com Ícone Auto-Theme")
        btn.setIcon(auto_icon)

        layout.addWidget(btn)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())