from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QTabWidget, QSizePolicy)

from controllers import wifi_controller
from misc import file_handler
from gui import primary_controls

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # // Main Window Settings // #
        # Screen Size
        self.showMaximized()
        self.setMinimumSize(1200, 800)

        # App Title
        self.setWindowTitle("FARTS/PEAR")

        # // Init Various Items // #
        # Config File
        config = file_handler.load_file("data/config.json")
        if config:
            print("present")

        # Load Stylesheet
        styleSheet = file_handler.load_file("data/dark_style.qss", as_json=False)
        if styleSheet:
            QApplication.instance().setStyleSheet(styleSheet)

        # Wi-Fi Access Point
        self.esp = wifi_controller.ESP32(tcp_port=config["TCP_PORT"], udp_port=config["UDP_PORT"],
                                          ip=config["ESP32_IP"])
        self.data_controller = wifi_controller.DataController(esp_instance=self.esp)
        self.data_controller.data_signal.connect(self.handle_new_data)
        self.data_controller.start()


        # Init tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        # Create Tabs
        self.primary_controls = primary_controls.PrimaryWindow(esp32=self.esp, config=config,
                                                               data_controller=self.data_controller)
        self.options_tab = None

        # Add tabs
        self.tabs.addTab(self.primary_controls, "Controller")
        self.tabs.addTab(self.options_tab, "Options")


    def handle_new_data(self, data):
        """Handles incoming data and updates UI components"""
        self.primary_controls.update_from_data(data)
