from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from source.extra_qwidgets.widgets.color_responsive_button import QColorResponsiveButton
from source.extra_qwidgets.utils import get_icon


class QCollapseGroup(QWidget):
    def __init__(self, title: str, widget: QWidget):
        super().__init__()
        self.__collapsed = False
        self.__widget = widget
        self.__widget.setContentsMargins(0, 0, 0, 0)
        self.__collapse_button = QColorResponsiveButton()
        self.__collapse_button.setIcon(get_icon("angle-down-solid.svg"))
        self.__collapse_button.setFlat(True)
        self.__collapse_button.clicked.connect(
            lambda: self.set_collapse(not self.__collapsed)
        )
        self.__label = QLabel(title)
        self.__header_layout = QHBoxLayout()
        self.__header_layout.addWidget(self.__collapse_button)
        self.__header_layout.addWidget(self.__label)
        self.__header_layout.setSpacing(10)
        self.__header_layout.setStretch(1, True)
        self.__layout = QVBoxLayout()
        self.__layout.setSpacing(0)
        self.__layout.addLayout(self.__header_layout)
        self.__layout.addWidget(widget)
        self.setLayout(self.__layout)

    def set_collapse(self, collapse: bool):
        if collapse:
            self.__widget.hide()
            self.__collapse_button.setIcon(get_icon("angle-right-solid.svg"))
        else:
            self.__widget.show()
            self.__collapse_button.setIcon(get_icon("angle-down-solid.svg"))
        self.__collapsed = collapse

    def widget(self):
        return self.__widget

    def header(self) -> QLabel:
        return self.__label