import socket, threading
from controllers import data_parser
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import json
import time

USE_REAL_DATA = False

class ESP32(QObject):
    """Handles ESP32 Signaling and Data Parsing"""
    # List of Signals to emit when data is parsed
    sensor_readings_S = pyqtSignal(dict)
    valve_state_S = pyqtSignal(dict)
    test_data_S = pyqtSignal(dict)
    warning_message_S = pyqtSignal(dict)

    def __init__(self, tcp_port, udp_port, ip):
        super().__init__()

        # // INIT Variables // #
        # Server info
        self.UDP_port = udp_port
        self.TCP_port = tcp_port
        self.ip = ip

        # Status info
        self.connected = False
        self.udp_thread = None
        self.udp_socket = None

    def connect(self):
        """Attempts to connect to available ESP32 through TCP and UDP"""
        # check if already connected
        if self.connected:
            return True

        # attempt connection
        try:
            # Check if esp is reachable with TCP
            # Create socket object with TCP connection
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_sock:
                test_sock.settimeout(2)
                test_sock.connect((self.ip, self.TCP_port))

            self.connected = True

            # Start UDP listener thread
            self.udp_thread = threading.Thread(target=self.receive_message, daemon=True)
            self.udp_thread.start()


        except Exception as e:
            return e

    def disconnect(self):
        """Manually disconnected from ESP"""
        if not self.connected:
            return
        self.connected = False

        # Close the UDP listener socket
        if self.udp_socket:
            self.udp_socket.close()
            self.udp_socket = None

    def receive_message(self):
        """Continuously receives UDP data"""
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(("0.0.0.0", self.UDP_port))

        while self.connected:
            try:
                data, addr = self.udp_socket.recv(1024)     # Buffer size
                data = data.decode()
                self.separator(data)


            except Exception as e:
                print(e)
                break

    def send_message(self, command):
        """Send a command over TCP"""
        if not self.connected:
            return

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
            try:
                tcp_sock.connect((self.ip, self.TCP_port))
                tcp_sock.sendall((command + "\n").encode())

            except Exception as e:
                print(e)

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



class DataController(QThread):
    data_signal = pyqtSignal(dict)  # Signal to send updated data

    def __init__(self, esp_instance=None):
        super().__init__()
        self.running = True
        self.esp_instance = esp_instance

    def run(self):
        while self.running:
            try:
                if USE_REAL_DATA and self.esp_instance:
                    # Get real data from ESP
                    self.esp_instance.sensor_readings.connect(self.data_signal.emit)

                else:
                    # Simulate real time data
                    simulated_data = {"x": [time.time()], "y": [self.simulated_sensor_value()]}
                    self.data_signal.emit(simulated_data)
            except Exception as e:
                print(f"Error reading JSON: {e}")
            time.sleep(1)  # Adjust based on how frequently you receive data

    def stop(self):
        self.running = False

    def simulated_sensor_value(self):
        """Generates fake sensor reading for sims"""
        return round(time.time() % 10, 2)