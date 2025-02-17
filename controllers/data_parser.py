from PyQt6.QtCore import pyqtSignal, QObject


class DataEmitter(QObject):
    """Class to emit PyQt Signals for parsed data"""


    def __init__(self):
        super().__init__()

    def separator(self, message):
        """Parses data into usable commands/info"""
        # List of available options
        signal_map = {
            "VALVES": self.valve_state_S,
            "SENSOR": self.sensor_readings_S,
            "TEST": self.test_data_S,
            "WARNING": self.warning_message_S,
        }

        # Circulate through your options
        for key, signal in signal_map.items():
            if key in message:
                signal.emit(message[key])

