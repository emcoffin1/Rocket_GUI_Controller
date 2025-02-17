from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtCore import QTimer
import pyqtgraph.opengl as gl
import time
import numpy as np
from stl import mesh
from pyqtgraph import Transform3D


class Rocket3DWidget(QWidget):
    """A QWidget-based 3D Rocket Model that can be embedded inside a tab."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumSize(200, 300)
        self.setMinimumSize(200, 300)
        # Create Layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 3D View Widget
        self.gl_widget = gl.GLViewWidget()
        layout.addWidget(self.gl_widget)

        # "Simulate Rotation" button
        self.simulate_button = QPushButton("Simulate Rotation")
        self.simulate_button.clicked.connect(self.toggle_fallback_mode)
        layout.addWidget(self.simulate_button)

        # Disable user-interactions
        self.gl_widget.mouseMoveEvent = lambda event: None
        self.gl_widget.mousePressEvent = lambda event: None
        self.gl_widget.wheelEvent = lambda event: None

        # Create the simple rocket shape
        self.create_rocket()

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
        self.setup_camera()

    def setup_camera(self):
        """Sets up initial camera angle for a slightly above perpendicular view."""
        self.gl_widget.opts['distance'] = 300  # Keep the camera back
        self.gl_widget.opts['elevation'] = 20  # Tilt slightly downward
        self.gl_widget.opts['azimuth'] = 90  # Keep looking from the front

    def create_rocket(self, filename="data/rocket_stl_test.stl", scale_factor=3):
        """Loads an STL file, scales it, and properly centers it for correct rotation and visibility."""

        # ✅ Load the STL File
        stl_mesh = mesh.Mesh.from_file(filename)

        # ✅ Extract Vertices & Faces
        vertices = stl_mesh.vectors.reshape(-1, 3)  # Convert 3D triangle array to flat vertex array
        faces = np.arange(len(vertices)).reshape(-1, 3)  # Generate face indices

        # ✅ Convert to NumPy Arrays for PyQtGraph
        vertices = np.array(vertices, dtype=np.float32)
        faces = np.array(faces, dtype=np.int32)

        # ✅ Compute Bounding Box
        min_bounds = np.min(vertices, axis=0)
        max_bounds = np.max(vertices, axis=0)
        center = (max_bounds + min_bounds) / 2

        # ✅ Compute Model Height (Before Scaling)
        model_height = max_bounds[2] - min_bounds[2]

        # ✅ Scale Model (Make It Larger)
        vertices = (vertices - center) * scale_factor  # Scale around the origin

        # ✅ Create MeshData for PyQtGraph
        mesh_data = gl.MeshData(vertexes=vertices, faces=faces)

        # ✅ Create the 3D Rocket Model
        self.rocket = gl.GLMeshItem(
            meshdata=mesh_data,
            smooth=True,
            drawEdges=False,
            shader='shaded',
            glOptions='opaque'
        )

        # ✅ Apply Initial Transformations
        self.rocket.rotate(90, 1, 0, 0)  # Fix STL orientation if needed

        # ✅ Manually Create a Transformation Matrix to Move the Rocket Up
        transform = Transform3D()
        transform.translate(0, 0, model_height * 0.5 * scale_factor)  # Adjust upward
        self.rocket.setTransform(transform)

        # ✅ Add to the Scene
        self.gl_widget.addItem(self.rocket)

    def update_view(self):
        """Applies pitch, yaw, and roll rotations to the rocket model."""
        # Check for connection loss (failsafe mode)
        if time.time() - self.last_data_timestamp > 2.5:
            self.fallback_mode = True  # Enable auto-rotation

        if self.fallback_mode:
            self.yaw = 0  # No yaw change in fallback mode
            self.pitch = 0  # No pitch change in fallback mode
            self.roll += 0.2  # Minor roll variation

        # Apply Rotation to Rocket
        self.rocket.resetTransform()
        self.rocket.rotate(self.roll, 0, 0, 1)  # Roll (Z-axis)
        self.rocket.rotate(self.pitch, 0, 1, 0)  # Pitch (Y-axis)
        self.rocket.rotate(self.yaw, 1, 0, 0)  # Pitch (X-axis)


    def toggle_fallback_mode(self):
        """Manually triggers the fallback mode for slow autorotation."""
        self.fallback_mode = not self.fallback_mode
