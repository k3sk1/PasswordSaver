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

BUTTON_STYLE2 = """
QPushButton {
    background-color: #d11a2a;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #e63946;
}
"""

BUTTON_STYLE_CIRCLE = """
QToolButton {
    border-radius: 20px;  /* Border-radius må være halvparten av bredden/høyden */
    border: 1px solid gray;
    min-width: 40px;  /* Juster disse verdiene for å gjøre knappen større/mindre */
    min-height: 40px;
    max-width: 40px;
    max-height: 40px;
    width: 40px;
    height: 40px;
    padding: 0;
    text-align: center;  /* Sentrer teksten */
}
"""


LABEL_STYLE = """
QLabel {
    font-weight: bold;
}
"""
