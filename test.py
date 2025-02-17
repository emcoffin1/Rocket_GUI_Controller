import sys
import socket
import threading
import json
import time
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from scipy.spatial.transform import Rotation as R

class ESP32Receiver(QObject):
    """Receives UDP JSON data from ESP32 and emits parsed pitch, yaw, roll."""
    data_received = pyqtSignal(float, float, float)  # Pitch, Yaw, Roll

    def __init__(self, udp_port=12345):
        super().__init__()
        self.udp_port = udp_port
        self.running = True
        self.thread = threading.Thread(target=self.receive_data, daemon=True)
        self.thread.start()

    def receive_data(self):
        """Receives UDP data and parses JSON."""
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(("0.0.0.0", self.udp_port))
        print(f"Listening for ESP32 JSON data on port {self.udp_port}...")

        while self.running:
            data, _ = udp_socket.recvfrom(1024)  # Receive up to 1024 bytes
            try:
                json_data = json.loads(data.decode().strip())
                pitch = float(json_data.get("pitch", 0))
                yaw = float(json_data.get("yaw", 0))
                roll = float(json_data.get("roll", 0))

                # Emit parsed data
                self.data_received.emit(pitch, yaw, roll)

            except json.JSONDecodeError:
                print(f"⚠️ Invalid JSON received: {data}")
            except Exception as e:
                print(f"⚠️ Error processing data: {e}")

    def stop(self):
        """Stops the UDP listener."""
        self.running = False


class Live3DModel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live 3D Model - Pitch/Yaw/Roll")
        self.setGeometry(100, 100, 800, 600)

        # Create UI layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        self.setCentralWidget(central_widget)
        central_widget.setLayout(layout)

        # 3D View Widget
        self.gl_widget = gl.GLViewWidget()
        layout.addWidget(self.gl_widget)

        # Add "Simulate Rotation" button
        self.simulate_button = QPushButton("Simulate Rotation")
        self.simulate_button.clicked.connect(self.toggle_fallback_mode)
        layout.addWidget(self.simulate_button)

        # Create a 3D mesh (Cube as placeholder for spacecraft)
        verts = np.array([
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # Bottom face
            [-1, -1,  1], [1, -1,  1], [1, 1,  1], [-1, 1,  1]   # Top face
        ])
        faces = np.array([
            [0, 1, 2], [2, 3, 0],  # Bottom
            [4, 5, 6], [6, 7, 4],  # Top
            [0, 1, 5], [5, 4, 0],  # Side 1
            [2, 3, 7], [7, 6, 2],  # Side 2
            [1, 2, 6], [6, 5, 1],  # Side 3
            [3, 0, 4], [4, 7, 3]   # Side 4
        ])
        colors = np.array([[1, 0, 0, 1] for _ in faces])  # Red color

        self.spacecraft = gl.GLMeshItem(vertexes=verts, faces=faces, faceColors=colors, smooth=False, drawEdges=True)
        self.gl_widget.addItem(self.spacecraft)

        # Create UDP Receiver
        self.receiver = ESP32Receiver()
        self.receiver.data_received.connect(self.update_orientation)

        # Timer for real-time updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_view)
        self.timer.start(50)  # Update every 50ms

        # Store rotation angles
        self.pitch = 0
        self.yaw = 0
        self.roll = 0
        self.last_data_timestamp = time.time()
        self.fallback_mode = False  # If True, the model will rotate on its own

    def update_orientation(self, pitch, yaw, roll):
        """Updates the stored pitch, yaw, and roll values."""
        self.pitch, self.yaw, self.roll = pitch, yaw, roll
        self.last_data_timestamp = time.time()  # Update last data time
        self.fallback_mode = False  # Disable fallback mode if data is received

    def update_view(self):
        """Applies pitch, yaw, and roll rotations to the spacecraft model."""
        # Check for connection loss (failsafe mode)
        if time.time() - self.last_data_timestamp > 2.5:
            self.fallback_mode = True  # Enable auto-rotation

        if self.fallback_mode:
            self.yaw += 1.0  # Slowly rotate in yaw
            self.pitch += 0.5  # Slight pitch variation
            self.roll += 0.2  # Minor roll variation

        # Compute rotation matrix using scipy
        rotation_matrix = R.from_euler('xyz', [self.roll, self.pitch, self.yaw], degrees=True).as_matrix()

        # Apply rotation to 3D object
        self.spacecraft.resetTransform()  # Reset previous transformations
        self.spacecraft.rotate(self.roll, 1, 0, 0)  # Roll (X-axis)
        self.spacecraft.rotate(self.pitch, 0, 1, 0)  # Pitch (Y-axis)
        self.spacecraft.rotate(self.yaw, 0, 0, 1)  # Yaw (Z-axis)
    def toggle_fallback_mode(self):
        """Allows user to manually trigger the fallback mode (slow rotation)."""
        self.fallback_mode = not self.fallback_mode
        if self.fallback_mode:
            print("✅ Manual Rotation Mode: ENABLED")
        else:
            print("❌ Manual Rotation Mode: DISABLED")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Live3DModel()
    window.show()
    sys.exit(app.exec())
