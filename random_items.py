from PyQt6.QtWidgets import (QLabel, QSizePolicy)
from PyQt6.QtGui import QFont


def label_maker(text, style="Helvetica", size=40, weight=QFont.Weight.Medium, ital=False, color="black"):
    """Creates a standard form QLabel with 20, black text"""
    label = QLabel(text)
    font = QFont()
    font.setWeight(weight)
    font.setItalic(ital)
    font.setPointSize(size)
    label.setFont(font)

    return label
