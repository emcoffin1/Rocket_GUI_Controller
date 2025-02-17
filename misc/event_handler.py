from misc import file_handler
from PyQt6.QtWidgets import QApplication

try:
    styleSheet = file_handler.load_file("data/dark_style.qss")


except Exception as e:
    print(e)