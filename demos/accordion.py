from qextrawidgets.widgets.miscellaneous.accordion.accordion_header import (
    QAccordionHeader,
)
import sys
import typing

from PySide6.QtCore import Qt, QEasingCurve
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QGroupBox,
    QRadioButton,
    QCheckBox,
    QLineEdit,
    QFormLayout,
    QTextEdit,
    QButtonGroup,
    QComboBox,
    QSpinBox,
)

from qextrawidgets.gui.icons import QThemeResponsiveIcon
from qextrawidgets.widgets.miscellaneous.accordion import QAccordion


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QAccordion Demo")
        self.resize(900, 700)

        # Try to load icon, fallback if utility is not configured
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        self._init_widgets()
        self.setup_layout()
        self.setup_connections()

        # --- Accordion Creation ---
        self.populate_accordion()

    def _init_widgets(self) -> None:
        self.accordion = QAccordion()

        # --- Group: Visibility ---
        self.button_expand = QPushButton("Expand All (expandAll)")

        self.button_collapse = QPushButton("Collapse All (collapseAll)")

        # --- Group: Icon Style ---
        self.button_group_style = QButtonGroup(self)
        self.radio_button_arrow = QRadioButton("Arrow")
        self.radio_button_arrow.setChecked(True)

        self.radio_button_plus = QRadioButton("Plus / Minus (+/-)")

        self.button_group_style.addButton(self.radio_button_arrow)
        self.button_group_style.addButton(self.radio_button_plus)

        # --- Group: Icon Position ---
        self.button_group_position = QButtonGroup(self)
        self.radio_button_left = QRadioButton("Left")
        self.radio_button_left.setChecked(True)

        self.radio_button_right = QRadioButton("Right")

        self.button_group_position.addButton(self.radio_button_left)
        self.button_group_position.addButton(self.radio_button_right)

        # --- Group: Content Alignment ---
        self.button_group_alignment = QButtonGroup(self)
        self.radio_button_top = QRadioButton("Top")
        self.radio_button_top.setChecked(True)

        self.radio_button_center = QRadioButton("Center")

        self.radio_button_bottom = QRadioButton("Bottom")

        self.button_group_alignment.addButton(self.radio_button_top)
        self.button_group_alignment.addButton(self.radio_button_center)
        self.button_group_alignment.addButton(self.radio_button_bottom)

        # --- Group: Appearance ---
        self.checkbox_flat = QCheckBox("Flat Mode (setFlat)")
        self.checkbox_auto_stretch = QCheckBox("Auto Stretch Expanded Items")
        self.checkbox_auto_stretch.setChecked(self.accordion.isAutoStretch())

        # --- Group: Scroll ---
        self.button_scroll_top = QPushButton("Reset Scroll (Top)")

        # Scroll to item 4 (long text)
        self.button_scroll_item = QPushButton("Scroll to Long Item")

        # --- Group: Animation ---
        self.checkbox_animation = QCheckBox("Enable Animation")

        self.label_duration = QLabel("Animation Duration")
        self.spinbox_duration = QSpinBox()
        self.spinbox_duration.setRange(50, 1000)
        self.spinbox_duration.setValue(200)
        self.spinbox_duration.setSingleStep(50)

        self.label_easing = QLabel("Animation Style")
        self.combobox_easing = QComboBox()
        self.combobox_easing.addItem("Linear", QEasingCurve.Type.Linear)
        self.combobox_easing.addItem("InOutQuad", QEasingCurve.Type.InOutQuad)
        self.combobox_easing.addItem(
            "InOutQuart (Padrão)", QEasingCurve.Type.InOutQuart
        )
        self.combobox_easing.addItem("OutCubic", QEasingCurve.Type.OutCubic)
        self.combobox_easing.addItem("InOutBack", QEasingCurve.Type.InOutBack)
        self.combobox_easing.addItem("OutBounce", QEasingCurve.Type.OutBounce)
        self.combobox_easing.addItem("OutElastic", QEasingCurve.Type.OutElastic)
        self.combobox_easing.setCurrentIndex(2)  # InOutQuart

    def setup_connections(self) -> None:
        # --- Group: Visibility ---
        self.button_expand.clicked.connect(self.accordion.expandAll)
        self.button_collapse.clicked.connect(self.accordion.collapseAll)

        # --- Group: Icon Style ---
        self.radio_button_arrow.toggled.connect(
            lambda checked: (
                self.accordion.setIconStyle(QAccordionHeader.IndicatorStyle.Arrow)
                if checked
                else None
            )
        )
        self.radio_button_plus.toggled.connect(
            lambda checked: (
                self.accordion.setIconStyle(QAccordionHeader.IndicatorStyle.PlusMinus)
                if checked
                else None
            )
        )

        # --- Group: Icon Position ---
        self.radio_button_left.toggled.connect(
            lambda checked: (
                self.accordion.setIconPosition(
                    QAccordionHeader.IconPosition.LeadingPosition
                )
                if checked
                else None
            )
        )
        self.radio_button_right.toggled.connect(
            lambda checked: (
                self.accordion.setIconPosition(
                    QAccordionHeader.IconPosition.TrailingPosition
                )
                if checked
                else None
            )
        )

        # --- Group: Content Alignment ---
        self.radio_button_top.toggled.connect(
            lambda checked: (
                self.accordion.setItemsAlignment(Qt.AlignmentFlag.AlignTop)
                if checked
                else None
            )
        )
        self.radio_button_center.toggled.connect(
            lambda checked: (
                self.accordion.setItemsAlignment(Qt.AlignmentFlag.AlignVCenter)
                if checked
                else None
            )
        )
        self.radio_button_bottom.toggled.connect(
            lambda checked: (
                self.accordion.setItemsAlignment(Qt.AlignmentFlag.AlignBottom)
                if checked
                else None
            )
        )

        # --- Group: Appearance ---
        self.checkbox_flat.toggled.connect(self.accordion.setFlat)
        self.checkbox_auto_stretch.toggled.connect(self.accordion.setAutoStretch)

        # --- Group: Scroll ---
        self.button_scroll_top.clicked.connect(self.accordion.resetScroll)
        self.button_scroll_item.clicked.connect(
            lambda: (
                self.item_long_text and self.accordion.scrollToItem(self.item_long_text)
            )
        )

        # --- Group: Animation ---
        self.checkbox_animation.toggled.connect(self.accordion.setAnimationEnabled)
        self.spinbox_duration.valueChanged.connect(self.accordion.setAnimationDuration)
        self.combobox_easing.currentIndexChanged.connect(
            lambda: self.accordion.setAnimationEasing(
                typing.cast(QEasingCurve.Type, self.combobox_easing.currentData())
            )
        )

    def setup_layout(self) -> None:
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # --- 2. Control Panel (Left Side) ---
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Group: Visibility ---
        group_box_visibility = QGroupBox("Global Visibility")
        layout_visibility = QVBoxLayout()
        layout_visibility.addWidget(self.button_expand)
        layout_visibility.addWidget(self.button_collapse)
        group_box_visibility.setLayout(layout_visibility)
        control_layout.addWidget(group_box_visibility)

        # --- Group: Icon Style ---
        group_box_style = QGroupBox("Icon Style (setIconStyle)")
        layout_style = QVBoxLayout()
        layout_style.addWidget(self.radio_button_arrow)
        layout_style.addWidget(self.radio_button_plus)
        group_box_style.setLayout(layout_style)
        control_layout.addWidget(group_box_style)

        # --- Group: Icon Position ---
        group_box_position = QGroupBox("Icon Position (setIconPosition)")
        layout_position = QVBoxLayout()
        layout_position.addWidget(self.radio_button_left)
        layout_position.addWidget(self.radio_button_right)
        group_box_position.setLayout(layout_position)
        control_layout.addWidget(group_box_position)

        # --- Group: Content Alignment ---
        group_box_alignment = QGroupBox("Content Alignment (setContentAlignment)")
        layout_alignment = QVBoxLayout()
        layout_alignment.addWidget(self.radio_button_top)
        layout_alignment.addWidget(self.radio_button_center)
        layout_alignment.addWidget(self.radio_button_bottom)
        group_box_alignment.setLayout(layout_alignment)
        control_layout.addWidget(group_box_alignment)

        # --- Group: Appearance ---
        group_box_appearance = QGroupBox("Appearance")
        layout_appearance = QVBoxLayout()
        layout_appearance.addWidget(self.checkbox_flat)
        layout_appearance.addWidget(self.checkbox_auto_stretch)
        group_box_appearance.setLayout(layout_appearance)
        control_layout.addWidget(group_box_appearance)

        # --- Group: Scroll ---
        group_box_scroll = QGroupBox("Scroll Test")
        layout_scroll = QVBoxLayout()
        layout_scroll.addWidget(self.button_scroll_top)
        layout_scroll.addWidget(self.button_scroll_item)
        group_box_scroll.setLayout(layout_scroll)
        control_layout.addWidget(group_box_scroll)

        # --- Group: Animation ---
        group_box_animation = QGroupBox("Animation")
        layout_animation = QVBoxLayout()
        layout_animation.addWidget(self.checkbox_animation)
        layout_animation.addWidget(self.label_duration)
        layout_animation.addWidget(self.spinbox_duration)
        layout_animation.addWidget(self.label_easing)
        layout_animation.addWidget(self.combobox_easing)
        group_box_animation.setLayout(layout_animation)
        control_layout.addWidget(group_box_animation)

        # Add to layout: Controls on left (1/3), Accordion on right (2/3)
        main_layout.addWidget(control_panel, 1)
        main_layout.addWidget(self.accordion, 2)

    def populate_accordion(self):
        """Adds varied sections to demonstrate versatility."""

        # 1. Simple Widget
        self.accordion.insertSection(
            "1. Introduction",
            QLabel(
                "This is a dynamic Accordion in PySide6.\\nUse the left panel to test."
            ),
        )

        # 2. Individual Configuration (Override)
        # Should this item obey global buttons if manually configured later?
        # Note: The global setIconPosition method iterates over all.
        # Here we just show that we can add and configure on the fly.
        label_custom = QLabel(
            "This item was added and configured individually\\nwith icon on the right initially."
        )
        item_custom = self.accordion.insertSection(
            "2. Manually Configured Item", label_custom
        )
        item_custom.setIconPosition(QAccordionHeader.IconPosition.TrailingPosition)

        # 3. Nested Layout (Buttons and actions)
        widget_actions = QWidget()
        layout_actions = QHBoxLayout(widget_actions)
        layout_actions.addWidget(QPushButton("Action 1"))
        layout_actions.addWidget(QPushButton("Action 2"))
        layout_actions.addWidget(QPushButton("Action 3"))
        self.accordion.insertSection("3. Button Container", widget_actions)

        # 4. Long Text (To test Scroll)
        long_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\\n" * 20
        text_edit = QTextEdit()
        text_edit.setPlainText(long_text)
        text_edit.setMinimumHeight(200)  # Force height to test accordion scroll
        self.item_long_text = self.accordion.insertSection(
            "4. Long Content (Scroll Test)", text_edit
        )

        # 5. Complex Form
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.addRow("Name:", QLineEdit())
        form_layout.addRow("Email:", QLineEdit())
        form_layout.addRow("Accept Terms:", QCheckBox())
        self.item_form = self.accordion.insertSection(
            "5. Registration Form", form_widget
        )

        # 6. More items to fill space
        for i in range(6, 10):
            self.accordion.insertSection(
                f"{i}. Extra Item", QLabel(f"Content of item {i}")
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
