from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QButtonGroup, QCheckBox, QComboBox)
from PyQt6.QtCore import Qt
from controllers import model_maker
from misc.random_items import label_maker



class PrimaryWindow(QWidget):
    def __init__(self, esp32, config):
        super().__init__()
        """Primary tab for displaying all rocket info"""
        # // INIT Random // #
        esp32 = esp32
        config = config
        # Ensure size is max

        # INIT Layout
        self.layout = QHBoxLayout()

        # INIT Splitters
        center_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Widgets for splitter
        right_side = RightHandController()
        left_side = LeftHandController()
        center_splitter.addWidget(left_side)
        center_splitter.addWidget(right_side)


        # Form Layout
        self.setGeometry(100, 100, 1200, 600)
        center_splitter.setSizes([600, 600])
        self.layout.addWidget(center_splitter)
        # Set layout
        self.setLayout(self.layout)


class RightHandController(QWidget):
    def __init__(self):
        super().__init__()
        """Will form the graph and location for 3d model"""
        # Splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side layout/widget
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # Right side layout/widget
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        # Items
        rocket = model_maker.Rocket3DWidget()
        option_panel = QButtonGroup()

        # // GRAPH SIDE // #
        # Graph options
        opt1 = QCheckBox("PvT")
        opt2 = QCheckBox("FvT")
        opt3 = QCheckBox("FvP")

        # Add options
        option_panel.addButton(opt1, 1)
        option_panel.addButton(opt2, 2)
        option_panel.addButton(opt3, 3)
        option_panel.setExclusive(False)

        # Add Label to the checkboxes
        top_check_layout_v = QVBoxLayout()
        label = label_maker(text="GRAPHS")
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        top_check_layout_v.addWidget(label)

        top_check_layout_h = QHBoxLayout()
        top_check_layout_h.addWidget(opt1)
        top_check_layout_h.addWidget(opt2)
        top_check_layout_h.addWidget(opt3)
        top_check_layout_v.addLayout(top_check_layout_h)
        top_check_layout_h.addStretch(1)
        left_layout.addLayout(top_check_layout_v)
        left_layout.addStretch(1)

        # // ROCKET SIDE // #
        # Test Picker
        combo = QComboBox()
        combo.addItem("No Test")
        combo.addItem("Leak Test")
        combo.addItem("Decay Test")
        combo.addItem("Click Test")
        combo.addItem("Igniter Test")
        right_layout.addWidget(combo)

        # Rocket
        right_layout.addWidget(rocket, alignment=Qt.AlignmentFlag.AlignHCenter)



        # // Splitter and layout format // #
        right_layout.addStretch(1)
        left_layout.addStretch(1)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([700,300])

        main_layout = QVBoxLayout()
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)


class LeftHandController(QWidget):
    def __init__(self):
        super().__init__()
        """Forms the left side controller with values"""

        # // Main Window // #
        right_layout = QVBoxLayout()

        # // ITEMS // #
        label = label_maker(text="TEST")
        right_layout.addWidget(label)

        self.setLayout(right_layout)








