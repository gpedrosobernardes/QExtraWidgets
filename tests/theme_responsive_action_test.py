import sys

from PySide6.QtWidgets import QMainWindow, QApplication, QMenu

from extra_qwidgets.widgets.theme_responsive_action import QThemeResponsiveAction
from source.extra_qwidgets.utils import colorize_icon_by_theme, get_awesome_icon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Theme Responsive Action Test")
        self.setWindowIcon(colorize_icon_by_theme(get_awesome_icon("python", "brands")))
        self.resize(250, 125)

        menu = QMenu("Social Media", self)

        facebook_action = QThemeResponsiveAction(self, text="Facebook")
        facebook_action.setIcon(get_awesome_icon("facebook", "brands"))
        github_action = QThemeResponsiveAction(self, text="Github")
        github_action.setIcon(get_awesome_icon("github", "brands"))

        menu.addAction(facebook_action)
        menu.addAction(github_action)

        menu_bar = self.menuBar()
        menu_bar.addMenu(menu)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())