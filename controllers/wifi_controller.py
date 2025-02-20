import socket, threading
from PyQt6.QtCore import QObject, pyqtSignal, QThread, Qt, QTimer, QMutex
import time
import random
from misc.file_handler import load_file

config = load_file("data/config.json")
USE_REAL_DATA = config["USE_REAL_DATA"]

class ESP32(QObject):
    """Handles ESP32 Signaling and Data Parsing"""
    data_list = pyqtSignal(dict)

    def __init__(self, tcp_port, udp_port, ip):
        super().__init__()
        self.UDP_port = udp_port
        self.TCP_port = tcp_port
        self.ip = ip
        self.connected = False
        self.udp_thread = None
        self.udp_socket = None

    def connect(self):
        """Attempts to connect to available ESP32 through TCP and UDP"""
        if self.connected:
            return True
        try:
            with socket.create_connection((self.ip, self.TCP_port), timeout=2):
                self.connected = True
                self.udp_thread = threading.Thread(target=self.receive_message, daemon=True)
                self.udp_thread.start()
        except Exception as e:
            print(f"Connection error: {e}")
            return e

    def disconnect(self):
        """Manually disconnect from ESP"""
        if not self.connected:
            return
        self.connected = False
        if self.udp_socket:
            self.udp_socket.close()
            self.udp_socket = None

    def receive_message(self):
        """Continuously receives UDP data with non-blocking socket"""
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.settimeout(1.0)  # Avoid blocking indefinitely
        self.udp_socket.bind(("0.0.0.0", self.UDP_port))
        while self.connected:
            try:
                data, _ = self.udp_socket.recvfrom(1024)  # Buffer size
                decoded_data = data.decode()
                if decoded_data:
                    self.data_list.emit(decoded_data)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Receive error: {e}")
                break

    def send_message(self, command):
        """Send a command over TCP"""
        if not self.connected:
            return
        try:
            with socket.create_connection((self.ip, self.TCP_port)) as tcp_sock:
                tcp_sock.sendall(f"{command}\n".encode())
        except Exception as e:
            print(f"Send error: {e}")


from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt, QMutex
import time
import random

class DataController(QThread):
    data_signal = pyqtSignal(dict)  # Signal to send updated data

    def __init__(self, esp_instance=None, update_interval=100):
        super().__init__()
        self.running = True
        self.esp_instance = esp_instance
        self.start_time = time.time()
        self.firing = False
        self.angle_value = 0
        self.angle_increasing = True
        self.update_interval = update_interval
        self.mutex = QMutex()  # Mutex to prevent data race conditions

        if not USE_REAL_DATA:
            self.timer = QTimer()
            self.timer.timeout.connect(self.send_data)
            self.timer.start(self.update_interval)

        if self.esp_instance:
            self.esp_instance.data_list.connect(self.process_real_data, type=Qt.ConnectionType.QueuedConnection)

    def run(self):
        while self.running:
            try:
                if USE_REAL_DATA and self.esp_instance and self.esp_instance.connected:
                    pass  # Real data is handled via signals
                else:
                    self.msleep(1)  # Prevent high CPU usage
            except Exception as e:
                print(f"datacontroller: {e}")

    def send_data(self):
        """Emit data at a controlled interval to prevent UI stuttering."""
        self.mutex.lock()
        simulated_data = {
            'time': [round(time.time() - self.start_time, 2)],
            'LMV': [self.simulated_sensor_value()],
            "Force": [self.simulated_sensor_value() / 5],
            'Pitch': [self.simulated_angle_value()]
        }
        self.data_signal.emit(simulated_data)
        self.mutex.unlock()

    def stop(self):
        self.running = False
        if not USE_REAL_DATA:
            self.timer.stop()

    def simulated_sensor_value(self):
        return round(random.uniform(1, 6), 2)

    def simulated_angle_value(self):
        """Oscillates between -180 and 180 degrees"""
        self.angle_value += 5 if self.angle_increasing else -5
        if self.angle_value >= 180 or self.angle_value <= -180:
            self.angle_increasing = not self.angle_increasing
        return self.angle_value

    def process_real_data(self, data):
        """Processes incoming real data without blocking the UI"""
        if isinstance(data, dict) and USE_REAL_DATA and self.esp_instance and self.esp_instance.connected:
            self.mutex.lock()
            self.data_signal.emit(data)
            self.mutex.unlock()
