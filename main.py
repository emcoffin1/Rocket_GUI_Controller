from gui import main_window
from PyQt6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    # Init app
    app = QApplication(sys.argv)

    # Open window
    window = main_window.MainWindow()
    window.show()

    # Close app
    sys.exit(app.exec())