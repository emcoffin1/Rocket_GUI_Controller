from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSlider
from PyQt6.QtCore import QTimer, Qt, QPointF
from PyQt6.QtGui import QPainter, QBrush, QColor, QTransform, QPixmap
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


class Rocket2DWidget_Pitch(QWidget):
    def __init__(self, pitch_angle=0):
        super().__init__()
        self.pitch_angle = pitch_angle  # Start with a neutral pitch

        self.setMinimumSize(50, 100)

    def set_pitch(self, angle):
        """Updates the pitch and refreshes the widget"""
        self.pitch_angle = angle
        self.update()  # Triggers a repaint

    def paintEvent(self, event):
        """Handles drawing the rocket with rotation"""
        print("Paint")
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # === Get Widget Center ===
        center_x = self.width() // 2
        center_y = self.height() // 2

        # === Apply Rotation Transformation ===
        transform = QTransform()
        transform.translate(center_x, center_y)  # Move pivot point to center
        transform.rotate(self.pitch_angle)  # Rotate around pivot
        transform.translate(-center_x, -center_y)  # Move back

        painter.setTransform(transform)

        # === Draw Rocket Body (Rectangle) ===
        rocket_width = 40
        rocket_height = 100

        body_rect = (center_x - rocket_width // 2, center_y - rocket_height // 2, rocket_width, rocket_height)

        painter.setBrush(QBrush(QColor("gray")))
        painter.drawRect(*body_rect)

        # === Draw Rocket Nose (Triangle) ===
        nose_points = [
            QPointF(center_x, center_y - rocket_height // 2 - 20),  # Top Point
            QPointF(center_x - rocket_width // 2, center_y - rocket_height // 2),  # Bottom Left
            QPointF(center_x + rocket_width // 2, center_y - rocket_height // 2)  # Bottom Right
        ]

        painter.setBrush(QBrush(QColor("red")))
        painter.drawPolygon(*nose_points)

        # === Draw Rocket Fins (Two Small Triangles) ===
        fin_size = 15
        fin_height = 30

        left_fin = [
            QPointF(center_x - rocket_width // 2, center_y + rocket_height // 2),  # Top
            QPointF(center_x - rocket_width // 2 - fin_size, center_y + rocket_height // 2 + fin_height),  # Bottom Left
            QPointF(center_x - rocket_width // 2, center_y + rocket_height // 2 + fin_height)  # Bottom Right
        ]

        right_fin = [
            QPointF(center_x + rocket_width // 2, center_y + rocket_height // 2),  # Top
            QPointF(center_x + rocket_width // 2 + fin_size, center_y + rocket_height // 2 + fin_height),
            # Bottom Right
            QPointF(center_x + rocket_width // 2, center_y + rocket_height // 2 + fin_height)  # Bottom Left
        ]

        painter.setBrush(QBrush(QColor("darkblue")))
        painter.drawPolygon(*left_fin)
        painter.drawPolygon(*right_fin)

        painter.end()



class Rocket2DImagePitch(QWidget):
    def __init__(self, image_path, scale=0.25, pitch_angle=0, rotate_start=0, color=None):
        super().__init__()
        self.scale = scale
        self.iterate = 0
        self.image = QPixmap(image_path)
        self.pitch_angle = pitch_angle  # Initial pitch

        #  Rotate image -90° (90° counterclockwise) at start
        transform = QTransform()
        transform.rotate(rotate_start)  # Counterclockwise rotation
        self.image = self.image.transformed(transform)

        #  Resize Image
        new_w = int(self.image.width() * scale)
        new_h = int(self.image.height() * scale)
        self.image = self.image.scaled(new_w, new_h)

        #  Ensure it shows up
        self.setMinimumSize(self.image.height(), self.image.height())

        # Create color mask
        if color:
            colored_image = self.image.copy()
            painter_image = QPainter(colored_image)

            # Set color
            color = QColor("darkblue")
            painter_image.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            painter_image.fillRect(colored_image.rect(), color)
            painter_image.end()

            # Save image
            self.image = colored_image

        self.start_timer()

    def change_pitch(self, esp=False):
        """Increase pitch angle by 1 degree every 2 seconds"""
        if not esp:
            if self.iterate == 1:
                self.pitch_angle += 5
                self.iterate = 0
            else:
                self.pitch_angle -= 5
                self.iterate = 1
        self.update()

    def paintEvent(self, event):
        """Draw the rotated image"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get image center for pivot
        center_x = self.width() // 2
        center_y = self.height() // 2

        # Apply rotation
        painter.translate(center_x, center_y)
        painter.rotate(self.pitch_angle)
        painter.translate(-center_x, -center_y)


        img_x = center_x - self.image.width() // 2
        img_y = center_y - self.image.height() // 2
        painter.drawPixmap(img_x, img_y, self.image)

        painter.end()

    def start_timer(self):
        """Start a timer that updates the pitch every 2 seconds"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.change_pitch)
        self.timer.start(100)
