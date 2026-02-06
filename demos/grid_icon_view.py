from PySide6.QtWidgets import QAbstractItemView
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFormLayout,
    QSpinBox,
    QDoubleSpinBox,
    QLabel,
    QGroupBox,
)
from PySide6.QtGui import (
    QStandardItemModel,
    QStandardItem,
    QIcon,
    QColor,
    QPixmap,
    QPainter,
    QLinearGradient,
    QFont,
    QBrush,
    QPen,
)
from PySide6.QtCore import QSize, Qt, QRect

from qextrawidgets.widgets.views.grid_icon_view import QGridIconView


def create_dummy_icon(base_color: QColor, text: str, size: int = 128) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Create a nice gradient
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0.0, base_color.lighter(130))
    gradient.setColorAt(1.0, base_color.darker(110))

    # Draw Background (Rounded)
    rect = pixmap.rect().adjusted(4, 4, -4, -4)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(gradient))
    painter.drawRoundedRect(rect, 16, 16)

    # Draw a subtle border
    painter.setPen(QPen(base_color.darker(120), 2))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(rect, 16, 16)

    # Draw Text
    painter.setPen(Qt.GlobalColor.white)
    font = QFont("Segoe UI", size // 3, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)

    painter.end()
    return QIcon(pixmap)


class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QGridIconView Demo")
        self.resize(1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # central_widget.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        # Main Layout (Horizontal)
        main_layout = QHBoxLayout(central_widget)

        # -----------------------
        # Side Panel (Controls)
        # -----------------------
        side_panel = QWidget()
        side_panel.setFixedWidth(250)
        side_layout = QVBoxLayout(side_panel)
        main_layout.addWidget(side_panel)

        # Config Group
        config_group = QGroupBox("View Configuration")
        config_layout = QFormLayout(config_group)

        # Icon Width
        self.spin_width = QSpinBox()
        self.spin_width.setRange(20, 500)
        self.spin_width.setValue(100)
        self.spin_width.valueChanged.connect(self.update_view_settings)
        config_layout.addRow("Icon Width:", self.spin_width)

        # Icon Height
        self.spin_height = QSpinBox()
        self.spin_height.setRange(20, 500)
        self.spin_height.setValue(100)
        self.spin_height.valueChanged.connect(self.update_view_settings)
        config_layout.addRow("Icon Height:", self.spin_height)

        # Margin
        self.spin_margin = QSpinBox()
        self.spin_margin.setRange(0, 50)
        self.spin_margin.setValue(16)
        self.spin_margin.valueChanged.connect(self.update_view_settings)
        config_layout.addRow("Margin:", self.spin_margin)

        # Internal Margin
        self.spin_internal_margin = QDoubleSpinBox()
        self.spin_internal_margin.setRange(0.0, 0.5)
        self.spin_internal_margin.setSingleStep(0.05)
        self.spin_internal_margin.setValue(0.1)
        self.spin_internal_margin.valueChanged.connect(self.update_view_settings)
        config_layout.addRow("Internal Margin:", self.spin_internal_margin)

        side_layout.addWidget(config_group)
        side_layout.addStretch()

        # -----------------------
        # Main View
        # -----------------------
        # Create the view
        self.view = QGridIconView()
        # self.view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.view.setIconSize(QSize(100, 100))
        self.view.setMargin(16)

        # Style the view to look modern
        self.view.setStyleSheet(
            """
            QGridIconView {
                background-color: #1e1e1e;
                border: none;
            }
        """
        )

        main_layout.addWidget(self.view)

        # Create a standard model
        self.model = QStandardItemModel()

        # Define a nice palette (Material Designish)
        palette = [
            "#f44336",
            "#e91e63",
            "#9c27b0",
            "#673ab7",
            "#3f51b5",
            "#2196f3",
            "#03a9f4",
            "#00bcd4",
            "#009688",
            "#4caf50",
            "#8bc34a",
            "#cddc39",
            "#ffeb3b",
            "#ffc107",
            "#ff9800",
            "#ff5722",
            "#795548",
            "#9e9e9e",
            "#607d8b",
        ]

        for i in range(50):
            color_hex = palette[i % len(palette)]
            base_color = QColor(color_hex)

            item = QStandardItem()
            item.setText(f"Item {i + 1}")
            item.setForeground(QBrush(QColor("#e0e0e0")))  # Light text for dark mode

            # Generate fancy icon
            icon = create_dummy_icon(base_color, str(i + 1))
            item.setIcon(icon)

            item.setEditable(False)
            self.model.appendRow(item)

        self.view.setModel(self.model)
        self.view.itemClicked.connect(lambda idx: print(f"Clicked: {idx.data()}"))

    def update_view_settings(self):
        width = self.spin_width.value()
        height = self.spin_height.value()
        margin = self.spin_margin.value()
        internal_margin = self.spin_internal_margin.value()

        self.view.setIconSize(QSize(width, height))
        self.view.setMargin(margin)

        # Update delegate
        delegate = self.view.itemDelegate()
        if delegate:
            delegate.setItemInternalMargin(internal_margin)
            self.view.viewport().update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())
