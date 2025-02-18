from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QButtonGroup, QCheckBox, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from controllers import model_maker
from misc.random_items import label_maker
import misc.file_handler
import controllers.graph_controller



class PrimaryWindow(QWidget):
    def __init__(self, esp32, config, data_controller):
        super().__init__()
        """Primary tab for displaying all rocket info"""
        # // INIT Random // #
        esp32 = esp32
        config = config
        self.data_controller = data_controller
        # Ensure size is max

        # INIT Layout
        self.layout = QHBoxLayout()

        # INIT Splitters
        center_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Widgets for splitter
        right_side = RightHandController(data_controller=self.data_controller)
        left_side = LeftHandController(data_controller=self.data_controller)
        center_splitter.addWidget(left_side)
        center_splitter.addWidget(right_side)


        # Form Layout
        self.setGeometry(100, 100, 1200, 600)
        center_splitter.setSizes([600, 600])
        self.layout.addWidget(center_splitter)
        # Set layout
        self.setLayout(self.layout)

    def update_from_data(self, data):
        pass

class RightHandController(QWidget):
    def __init__(self, data_controller):
        super().__init__()
        """Will form the graph and location for 3d model"""
        self.data_controller = data_controller
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

        # Make the graphs
        self.graph_list = []
        table_test = controllers.graph_controller.GraphWidget(title="Test", x_lab="time", y_lab="LMV",
                                                              data_controller=self.data_controller)
        self.graph_list.append(table_test)

        force_time_graph = controllers.graph_controller.GraphWidget(title="Force v Time", x_lab="time", y_lab='Force',
                                                                    data_controller=self.data_controller)
        self.graph_list.append(force_time_graph)

        pitch_graph = controllers.graph_controller.GraphWidget(title="Pitch", x_lab="time", y_lab="Pitch",
                                                                    data_controller=self.data_controller
                                                                    )
        self.graph_list.append(pitch_graph)


        top_check_layout_v.addWidget(force_time_graph)
        top_check_layout_v.addWidget(table_test)
        top_check_layout_v.addWidget(pitch_graph)

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
        pitch_file = misc.file_handler.get_file_path("data/images/rocket_side_profile_pointed.png")
        rocket_pitch = model_maker.Rocket2DImagePitch(image_path=str(pitch_file), rotate_start=90)
        right_layout.addWidget(rocket_pitch, alignment=Qt.AlignmentFlag.AlignHCenter)
        pitch_label = label_maker("Pitch", size=10)
        right_layout.addWidget(pitch_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        roll_file = misc.file_handler.get_file_path("data/images/rocket_top_profile.png")
        rocket_roll = model_maker.Rocket2DImagePitch(image_path=str(roll_file), scale=0.5)
        right_layout.addWidget(rocket_roll, alignment=Qt.AlignmentFlag.AlignHCenter)
        roll_label = label_maker("Roll", size=10)
        right_layout.addWidget(roll_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # // Splitter and layout format // #
        right_layout.addStretch(1)
        left_layout.addStretch(1)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([700,300])

        main_layout = QVBoxLayout()
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

        # Connect datacontroller signal to graphs
        self.data_controller.data_signal.connect(self.update_graphs)

    def update_graphs(self, data):
        """Checks if new data has relevant keys for graph and update"""
        for graph in self.graph_list:
            if graph.x_l in data and graph.y_l in data:
                graph.update_data(data[graph.x_l], data[graph.y_l])


class LeftHandController(QWidget):
    def __init__(self, data_controller):
        super().__init__()
        """Forms the left side controller with values"""
        # Data updater
        self.data_controller = data_controller


        # // Main Window // #
        right_layout = QVBoxLayout()

        # // ITEMS // #
        label = label_maker(text="TEST")
        right_layout.addWidget(label)

        self.graph_list = []
        # Connect datacontroller signal to graphs
        self.data_controller.data_signal.connect(self.update_graphs)

    def update_graphs(self, data):
        """Checks if new data has relevant keys for graph and update"""
        for graph in self.graph_list:
            if graph.x_l in data and graph.y_l in data:
                graph.update_data(data[graph.x_l], data[graph.y_l])








