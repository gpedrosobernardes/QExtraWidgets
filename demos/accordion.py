import sys

from PySide6.QtCore import Qt, QEasingCurve
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QLabel, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QGroupBox, QRadioButton,
    QCheckBox, QLineEdit, QFormLayout, QTextEdit, QButtonGroup, QComboBox, QSpinBox
)

from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.widgets.accordion_item import QAccordionHeader
from qextrawidgets.widgets.accordion import QAccordion


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QAccordion Demo")
        self.resize(900, 700)

        # Try to load icon, fallback if utility is not configured
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        # Main Widget
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # --- 1. Accordion Creation ---
        self.accordion = QAccordion()
        self.populate_accordion()

        # --- 2. Control Panel (Left Side) ---
        control_panel = self.create_control_panel()

        # Add to layout: Controls on left (1/3), Accordion on right (2/3)
        main_layout.addWidget(control_panel, 1)
        main_layout.addWidget(self.accordion, 2)

        self.setCentralWidget(main_widget)

    def create_control_panel(self) -> QWidget:
        """Creates a side panel to test public Accordion functions."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Group: Visibility ---
        grp_vis = QGroupBox("Global Visibility")
        v_layout = QVBoxLayout()

        btn_expand = QPushButton("Expand All (expandAll)")
        btn_expand.clicked.connect(self.accordion.expandAll)

        btn_collapse = QPushButton("Collapse All (collapseAll)")
        btn_collapse.clicked.connect(self.accordion.collapseAll)

        v_layout.addWidget(btn_expand)
        v_layout.addWidget(btn_collapse)
        grp_vis.setLayout(v_layout)
        layout.addWidget(grp_vis)

        # --- Group: Icon Style ---
        grp_style = QGroupBox("Icon Style (setIconStyle)")
        v_style = QVBoxLayout()
        bg_style = QButtonGroup(self)

        rb_arrow = QRadioButton("Arrow")
        rb_arrow.setChecked(True)
        rb_arrow.toggled.connect(lambda checked: self.accordion.setIconStyle(QAccordionHeader.IndicatorStyle.Arrow) if checked else None)

        rb_plus = QRadioButton("Plus / Minus (+/-)")
        rb_plus.toggled.connect(lambda checked: self.accordion.setIconStyle(QAccordionHeader.IndicatorStyle.PlusMinus) if checked else None)

        bg_style.addButton(rb_arrow)
        bg_style.addButton(rb_plus)
        v_style.addWidget(rb_arrow)
        v_style.addWidget(rb_plus)
        grp_style.setLayout(v_style)
        layout.addWidget(grp_style)

        # --- Group: Icon Position ---
        grp_pos = QGroupBox("Icon Position (setIconPosition)")
        v_pos = QVBoxLayout()
        bg_pos = QButtonGroup(self)

        rb_left = QRadioButton("Left")
        rb_left.setChecked(True)
        rb_left.toggled.connect(lambda: self.accordion.setIconPosition(QAccordionHeader.IconPosition.LeadingPosition))

        rb_right = QRadioButton("Right")
        rb_right.toggled.connect(lambda: self.accordion.setIconPosition(QAccordionHeader.IconPosition.TrailingPosition))

        bg_pos.addButton(rb_left)
        bg_pos.addButton(rb_right)
        v_pos.addWidget(rb_left)
        v_pos.addWidget(rb_right)
        grp_pos.setLayout(v_pos)
        layout.addWidget(grp_pos)

        # --- Group: Appearance ---
        grp_look = QGroupBox("Appearance")
        v_look = QVBoxLayout()

        chk_flat = QCheckBox("Flat Mode (setFlat)")
        chk_flat.toggled.connect(self.accordion.setFlat)

        v_look.addWidget(chk_flat)
        grp_look.setLayout(v_look)
        layout.addWidget(grp_look)

        # --- Group: Scroll ---
        grp_scroll = QGroupBox("Scroll Test")
        v_scroll = QVBoxLayout()

        btn_scroll_top = QPushButton("Reset Scroll (Top)")
        btn_scroll_top.clicked.connect(self.accordion.resetScroll)

        # Scroll to item 4 (long text)
        btn_scroll_item = QPushButton("Scroll to Long Item")
        btn_scroll_item.clicked.connect(
            lambda: self.accordion.scrollToItem(self.item_long_text)
        )

        v_scroll.addWidget(btn_scroll_top)
        v_scroll.addWidget(btn_scroll_item)
        grp_scroll.setLayout(v_scroll)
        layout.addWidget(grp_scroll)

        # --- Group: Animation ---
        grp_anim = QGroupBox("Animation")
        v_anim = QVBoxLayout()

        check_animation = QCheckBox("Enable Animation")
        check_animation.setChecked(True)
        check_animation.toggled.connect(self.accordion.setAnimationEnabled)
        v_anim.addWidget(check_animation)

        v_anim.addWidget(QLabel("Animation Duration"))

        spin_duration = QSpinBox()
        spin_duration.setRange(50, 1000)
        spin_duration.setValue(200)
        spin_duration.setSingleStep(50)
        spin_duration.valueChanged.connect(self.accordion.setAnimationDuration)
        v_anim.addWidget(spin_duration)

        v_anim.addWidget(QLabel("Animation Style"))
        combo_easing = QComboBox()
        combo_easing.addItem("Linear", QEasingCurve.Type.Linear)
        combo_easing.addItem("InOutQuad", QEasingCurve.Type.InOutQuad)
        combo_easing.addItem("InOutQuart (Padrão)", QEasingCurve.Type.InOutQuart)
        combo_easing.addItem("OutCubic", QEasingCurve.Type.OutCubic)
        combo_easing.addItem("InOutBack", QEasingCurve.Type.InOutBack)
        combo_easing.addItem("OutBounce", QEasingCurve.Type.OutBounce)
        combo_easing.addItem("OutElastic", QEasingCurve.Type.OutElastic)
        combo_easing.setCurrentIndex(2)  # InOutQuart
        combo_easing.currentIndexChanged.connect(lambda: self.accordion.setAnimationEasing(combo_easing.currentData()))

        v_anim.addWidget(combo_easing)

        grp_anim.setLayout(v_anim)
        layout.addWidget(grp_anim)

        return panel

    def populate_accordion(self):
        """Adds varied sections to demonstrate versatility."""

        # 1. Simple Widget
        self.accordion.insertSection("1. Introduction", QLabel(
            "This is a dynamic Accordion in PySide6.\nUse the left panel to test."))

        # 2. Individual Configuration (Override)
        # Should this item obey global buttons if manually configured later?
        # Note: The global setIconPosition method iterates over all.
        # Here we just show that we can add and configure on the fly.
        lbl_custom = QLabel(
            "This item was added and configured individually\nwith icon on the right initially.")
        item_custom = self.accordion.insertSection("2. Manually Configured Item", lbl_custom)
        item_custom.setIconPosition("right")

        # 3. Nested Layout (Buttons and actions)
        widget_actions = QWidget()
        layout_actions = QHBoxLayout(widget_actions)
        layout_actions.addWidget(QPushButton("Action 1"))
        layout_actions.addWidget(QPushButton("Action 2"))
        layout_actions.addWidget(QPushButton("Action 3"))
        self.accordion.insertSection("3. Button Container", widget_actions)

        # 4. Long Text (To test Scroll)
        long_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n" * 20
        txt_edit = QTextEdit()
        txt_edit.setPlainText(long_text)
        txt_edit.setMinimumHeight(200)  # Force height to test accordion scroll
        self.item_long_text = self.accordion.insertSection("4. Long Content (Scroll Test)", txt_edit)

        # 5. Complex Form
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.addRow("Name:", QLineEdit())
        form_layout.addRow("Email:", QLineEdit())
        form_layout.addRow("Accept Terms:", QCheckBox())
        self.item_form = self.accordion.insertSection("5. Registration Form", form_widget)

        # 6. More items to fill space
        for i in range(6, 10):
            self.accordion.insertSection(f"{i}. Extra Item", QLabel(f"Content of item {i}"))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())