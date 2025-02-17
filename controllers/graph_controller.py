from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QGraphicsDropShadowEffect, QMenu)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


class GraphWidget(QWidget):
    def __init__(self, data_controller, title=None, x_lab=None, y_lab=None, parent=None, bg_color='#242424', x=None, y=None,
                 time_window=10):
        super().__init__(parent)
        self.data_controller = data_controller
        #self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.setMaximumHeight(200)
        if self.data_controller:
            self.data_controller.data_signal.connect(self.handle_new_data)


        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)  # Compact toolbar
        self.toolbar.setFixedHeight(20)  # Reduce toolbar size
        self.toolbar.hide()
        self.figure.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(5)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        # Layout: Put graph and toolbar on same row for compactness
        layout = QVBoxLayout()
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(self.toolbar)
        toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align to left for a compact feel

        layout.addLayout(toolbar_layout)
        layout.addWidget(self.canvas)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.x_data = x if x else []
        self.y_data = y if y else []
        self.title = title
        self.x_l = x_lab
        self.y_l = y_lab
        self.time_window = time_window
        self.manual_scroll = False

        # Detect manual user scroll
        self.canvas.mpl_connect("button_press_event", self.on_mouse_press)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.plot_graph()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        toggle_toolbar_action = menu.addAction("Toggle Toolbar")
        action = menu.exec(self.mapToGlobal(pos))
        if action == toggle_toolbar_action:
            if self.toolbar.isVisible():
                self.toolbar.hide()
            else:
                self.toolbar.show()

    def handle_new_data(self, data):
        if self.x_l in data and self.y_l in data:
            self.update_data(data[self.x_l], data[self.y_l])

    def on_mouse_press(self, event):
        """Detects if the user has clicked to pan or zoom, stopping auto-scroll."""
        if event.button == 1:  # Left mouse button
            self.manual_scroll = True

        else:
            pass

    def plot_graph(self):
        self.ax.clear()
        self.ax.set_facecolor('#242424')
        if self.x_data and self.y_data:
            self.ax.plot(self.x_data, self.y_data, linestyle='-', color='yellow', linewidth=0.5)

            if not self.manual_scroll:
                latest_time = self.x_data[-1]
                start_time = max(0, latest_time - self.time_window)
                self.ax.set_xlim(start_time-1, latest_time)

        self.ax.set_title(f"{self.title}", color='white', fontsize=7)
        self.ax.set_xlabel(f"{self.x_l}", color='white', fontsize=6)
        self.ax.set_ylabel(f"{self.y_l}", color='white', fontsize=6)
        self.ax.tick_params(colors='white', labelsize=5)

        self.figure.tight_layout(pad=0)

        self.canvas.draw()

    def update_data(self, x_data, y_data):
        self.x_data.extend(x_data)
        self.y_data.extend(y_data)

        if self.manual_scroll:
            latest_time = self.x_data[-1]
            current_xlim = self.ax.get_xlim()
            if latest_time > current_xlim[1]:
                self.manual_scroll = False

        self.plot_graph()
