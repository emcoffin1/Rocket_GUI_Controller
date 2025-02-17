import socket, threading
from controllers import data_parser
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import json
import time
import random
from misc.file_handler import load_file

config = load_file("data/config.json")
USE_REAL_DATA = config["USE_REAL_DATA"]

class ESP32(QObject):
    """Handles ESP32 Signaling and Data Parsing"""
    # List of Signals to emit when data is parsed
    data_list = pyqtSignal(dict)

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
                self.data_list.emit(data)


            except Exception as e:
                print(f"recieve_message:{e}")
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



class DataController(QThread):
    data_signal = pyqtSignal(dict)  # Signal to send updated data

    def __init__(self, esp_instance=None):
        super().__init__()
        self.running = True
        self.esp_instance = esp_instance
        self.start_time = time.time()
        self.firing = False
        self.angle_value = 0
        self.angle_increasing = True
        if self.esp_instance:
            self.esp_instance.data_list.connect(self.process_real_data)


    def run(self):
        while self.running:
            try:
                if USE_REAL_DATA:
                    if self.esp_instance and self.esp_instance.connected:
                        pass    # Data will be recieved from ESP32

                    else:
                        pass
                        # Get real data from ESP
                else:
                    simulated_data = {
                        'time': [round(time.time()-self.start_time,2)],
                        'LMV': [self.simulated_sensor_value()],
                        "Force": [self.simulated_sensor_value() / 5],
                        'Pitch': [self.simulated_angle_value()]
                    }
                    print(simulated_data)
                    self.data_signal.emit(simulated_data)
            except Exception as e:
                print(f"datacontroller: {e}")
            time.sleep(1)  # Adjust based on how frequently you receive data

    def stop(self):
        self.running = False

    def simulated_sensor_value(self):
        return round(random.uniform(1, 6), 2)

    def simulated_angle_value(self):
        """Oscillates between -180 and 180 degrees"""
        if self.angle_increasing:
            self.angle_value += 5
            if self.angle_value >= 180:
                self.angle_increasing = False
        else:
            self.angle_value -= 5
            if self.angle_value <= -180:
                self.angle_increasing = True
        return self.angle_value

    def process_real_data(self, data):
        if USE_REAL_DATA and self.esp_instance and self.esp_instance.connected:
            self.data_signal.emit(data)


