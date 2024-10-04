from PySide2.QtGui import QFont

# Definer global font
GLOBAL_FONT = QFont("Verdana", 16)

# Definer stilark uten font-family og font-size
LINE_EDIT_STYLE = """
QLineEdit {
    border: 1px solid #ccc;
    border-radius: 5px;
    padding: 10px;
}
"""


BUTTON_STYLE = """
QPushButton {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #45a049;
}
"""

LABEL_STYLE = """
QLabel {
    font-weight: bold;
}
"""
