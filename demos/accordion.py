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
        self.btn_expand = QPushButton("Expand All (expandAll)")

        self.btn_collapse = QPushButton("Collapse All (collapseAll)")

        # --- Group: Icon Style ---
        self.bg_style = QButtonGroup(self)
        self.rb_arrow = QRadioButton("Arrow")
        self.rb_arrow.setChecked(True)

        self.rb_plus = QRadioButton("Plus / Minus (+/-)")

        self.bg_style.addButton(self.rb_arrow)
        self.bg_style.addButton(self.rb_plus)

        # --- Group: Icon Position ---
        self.bg_pos = QButtonGroup(self)
        self.rb_left = QRadioButton("Left")
        self.rb_left.setChecked(True)

        self.rb_right = QRadioButton("Right")

        self.bg_pos.addButton(self.rb_left)
        self.bg_pos.addButton(self.rb_right)

        # --- Group: Content Alignment ---
        self.bg_align = QButtonGroup(self)
        self.rb_top = QRadioButton("Top")
        self.rb_top.setChecked(True)

        self.rb_center = QRadioButton("Center")

        self.rb_bottom = QRadioButton("Bottom")

        self.bg_align.addButton(self.rb_top)
        self.bg_align.addButton(self.rb_center)
        self.bg_align.addButton(self.rb_bottom)

        # --- Group: Appearance ---
        self.chk_flat = QCheckBox("Flat Mode (setFlat)")

        # --- Group: Scroll ---
        self.btn_scroll_top = QPushButton("Reset Scroll (Top)")

        # Scroll to item 4 (long text)
        self.btn_scroll_item = QPushButton("Scroll to Long Item")

        # --- Group: Animation ---
        self.check_animation = QCheckBox("Enable Animation")

        self.lbl_duration = QLabel("Animation Duration")
        self.spin_duration = QSpinBox()
        self.spin_duration.setRange(50, 1000)
        self.spin_duration.setValue(200)
        self.spin_duration.setSingleStep(50)

        self.lbl_easing = QLabel("Animation Style")
        self.combo_easing = QComboBox()
        self.combo_easing.addItem("Linear", QEasingCurve.Type.Linear)
        self.combo_easing.addItem("InOutQuad", QEasingCurve.Type.InOutQuad)
        self.combo_easing.addItem("InOutQuart (Padrão)", QEasingCurve.Type.InOutQuart)
        self.combo_easing.addItem("OutCubic", QEasingCurve.Type.OutCubic)
        self.combo_easing.addItem("InOutBack", QEasingCurve.Type.InOutBack)
        self.combo_easing.addItem("OutBounce", QEasingCurve.Type.OutBounce)
        self.combo_easing.addItem("OutElastic", QEasingCurve.Type.OutElastic)
        self.combo_easing.setCurrentIndex(2)  # InOutQuart

    def setup_connections(self) -> None:
        # --- Group: Visibility ---
        self.btn_expand.clicked.connect(self.accordion.expandAll)
        self.btn_collapse.clicked.connect(self.accordion.collapseAll)

        # --- Group: Icon Style ---
        self.rb_arrow.toggled.connect(
            lambda checked: (
                self.accordion.setIconStyle(QAccordionHeader.IndicatorStyle.Arrow)
                if checked
                else None
            )
        )
        self.rb_plus.toggled.connect(
            lambda checked: (
                self.accordion.setIconStyle(QAccordionHeader.IndicatorStyle.PlusMinus)
                if checked
                else None
            )
        )

        # --- Group: Icon Position ---
        self.rb_left.toggled.connect(
            lambda checked: (
                self.accordion.setIconPosition(
                    QAccordionHeader.IconPosition.LeadingPosition
                )
                if checked
                else None
            )
        )
        self.rb_right.toggled.connect(
            lambda checked: (
                self.accordion.setIconPosition(
                    QAccordionHeader.IconPosition.TrailingPosition
                )
                if checked
                else None
            )
        )

        # --- Group: Content Alignment ---
        self.rb_top.toggled.connect(
            lambda checked: (
                self.accordion.setItemsAlignment(Qt.AlignmentFlag.AlignTop)
                if checked
                else None
            )
        )
        self.rb_center.toggled.connect(
            lambda checked: (
                self.accordion.setItemsAlignment(Qt.AlignmentFlag.AlignVCenter)
                if checked
                else None
            )
        )
        self.rb_bottom.toggled.connect(
            lambda checked: (
                self.accordion.setItemsAlignment(Qt.AlignmentFlag.AlignBottom)
                if checked
                else None
            )
        )

        # --- Group: Appearance ---
        self.chk_flat.toggled.connect(self.accordion.setFlat)

        # --- Group: Scroll ---
        self.btn_scroll_top.clicked.connect(self.accordion.resetScroll)
        self.btn_scroll_item.clicked.connect(
            lambda: self.item_long_text
            and self.accordion.scrollToItem(self.item_long_text)
        )

        # --- Group: Animation ---
        self.check_animation.toggled.connect(self.accordion.setAnimationEnabled)
        self.spin_duration.valueChanged.connect(self.accordion.setAnimationDuration)
        self.combo_easing.currentIndexChanged.connect(
            lambda: self.accordion.setAnimationEasing(
                typing.cast(QEasingCurve.Type, self.combo_easing.currentData())
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
        grp_vis = QGroupBox("Global Visibility")
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.btn_expand)
        v_layout.addWidget(self.btn_collapse)
        grp_vis.setLayout(v_layout)
        control_layout.addWidget(grp_vis)

        # --- Group: Icon Style ---
        grp_style = QGroupBox("Icon Style (setIconStyle)")
        v_style = QVBoxLayout()
        v_style.addWidget(self.rb_arrow)
        v_style.addWidget(self.rb_plus)
        grp_style.setLayout(v_style)
        control_layout.addWidget(grp_style)

        # --- Group: Icon Position ---
        grp_pos = QGroupBox("Icon Position (setIconPosition)")
        v_pos = QVBoxLayout()
        v_pos.addWidget(self.rb_left)
        v_pos.addWidget(self.rb_right)
        grp_pos.setLayout(v_pos)
        control_layout.addWidget(grp_pos)

        # --- Group: Content Alignment ---
        grp_align = QGroupBox("Content Alignment (setContentAlignment)")
        v_align = QVBoxLayout()
        v_align.addWidget(self.rb_top)
        v_align.addWidget(self.rb_center)
        v_align.addWidget(self.rb_bottom)
        grp_align.setLayout(v_align)
        control_layout.addWidget(grp_align)

        # --- Group: Appearance ---
        grp_look = QGroupBox("Appearance")
        v_look = QVBoxLayout()
        v_look.addWidget(self.chk_flat)
        grp_look.setLayout(v_look)
        control_layout.addWidget(grp_look)

        # --- Group: Scroll ---
        grp_scroll = QGroupBox("Scroll Test")
        v_scroll = QVBoxLayout()
        v_scroll.addWidget(self.btn_scroll_top)
        v_scroll.addWidget(self.btn_scroll_item)
        grp_scroll.setLayout(v_scroll)
        control_layout.addWidget(grp_scroll)

        # --- Group: Animation ---
        grp_anim = QGroupBox("Animation")
        v_anim = QVBoxLayout()
        v_anim.addWidget(self.check_animation)
        v_anim.addWidget(self.lbl_duration)
        v_anim.addWidget(self.spin_duration)
        v_anim.addWidget(self.lbl_easing)
        v_anim.addWidget(self.combo_easing)
        grp_anim.setLayout(v_anim)
        control_layout.addWidget(grp_anim)

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
        lbl_custom = QLabel(
            "This item was added and configured individually\\nwith icon on the right initially."
        )
        item_custom = self.accordion.insertSection(
            "2. Manually Configured Item", lbl_custom
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
        txt_edit = QTextEdit()
        txt_edit.setPlainText(long_text)
        txt_edit.setMinimumHeight(200)  # Force height to test accordion scroll
        self.item_long_text = self.accordion.insertSection(
            "4. Long Content (Scroll Test)", txt_edit
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
