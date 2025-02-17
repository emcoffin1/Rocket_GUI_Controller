from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtGui import QFont

def label_maker(text, style="Helvetica", size=20, weight=QFont.Weight.Medium, ital=False, color="black"):
    """Creates a standard QLabel with customizable font, weight, and color."""
    label = QLabel(text)

    # ✅ Create font settings
    font = QFont(style, size)
    font.setWeight(weight)
    font.setItalic(ital)
    label.setFont(font)

    # ✅ Ensure color is applied
    label.setStyleSheet(f"color: {color};")

    return label

