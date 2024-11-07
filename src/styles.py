from PySide2.QtGui import QFont

# Global font
GLOBAL_FONT = QFont("Verdana", 16)

# Define themes with color palettes
THEMES = {
    "default": {
        "background": "#73777C",  # Bakgrunnsfargen for hovedvinduet (Central widget) #fcd4a0
        "stack_background": "#73777C",  # Bakgrunnsfargen for innloggings widget og blir også rammen rundt de andre widgetene.
        "button_hover_color": "#444444",  # (svart)
        "button_hover_color_1": "#4CAF50",  # (grønn)
        "button_hover_color_2": "#D32F2F",  # (rød)
        "button_style_background": "#2E2E2E",  # Bakgrunnsfarge for knapper (Grå)
        "button_style_circle_background": "#a6c4be",  # bakgrunnsfarge på sirkel knapp med solbriller/øye
        "button_text": "#ffffff",  # Tekstfarge for knapper (hvit)
        "button_mode_unchecked_1": "#a6c4be",  # lav passordstyrke knapp
        "button_mode_unchecked_2": "#a6c4be",  # medium passordstyrke knapp
        "button_mode_unchecked_3": "#a6c4be",  # høy passordstyrke knapp
        "button_mode_checked_1": "#FF6347",  # lav passordstyrke knapp
        "button_mode_checked_2": "#FFD700",  # medium passordstyrke knapp
        "button_mode_checked_3": "#32CD32",  # høy passordstyrke knapp
        "input_background": "#ffffff",  # Bakgrunnsfarge for inndatafelter (QLineEdit)
        "widget_background": "#b4a19e",  # Bakgrunnsfarge for widgets generelt
        "side_panel_background": "#a6c4be",  # Side panel background color
        "side_panel_border": "5px solid #2E2E2E",  # Kantlinje (border) rundt sidepanelet
        "label_text_color": "#ffffff",  # label tekst farge
        "label_background": "#2E2E2E",  # label bakgrunnsfarge
        # Farger for tabellstiler
        "header_background_table": "#2E2E2E",  # Bakgrunnsfarge for tabellhoder "#3C3F41"
        "header_text_color_table": "#FFFFFF",  # Tekstfarge for tabellhoder
        "header_border_color_table": "#2E2E2E",  # Kantfarge for tabellhoder
        "row_background_table": "#FFFFFF",  # Bakgrunnsfarge for tabellrader
        "row_text_color_table": "#444444",  # Tekstfarge for tabellrader
        "selected_row_background_table": "#4CAF50",  # Bakgrunnsfarge for valgte tabellrader
        "selected_row_text_color_table": "#FFFFFF",  # Tekstfarge for valgte tabellrader
    },
    "vintage": {
        "background": "#a3f08e",  # Bakgrunnsfargen for hovedvinduet (Central widget)
        "stack_background": "#e0cda9",  # Bakgrunnsfargen for QStackedWidget
        "button_hover_color": "#f08edb",  # Standard tekstfarge som brukes på etiketter, knapper, etc.
        "button_hover_color_1": "#4CAF50",  # (grønn)
        "button_hover_color_2": "#D32F2F",  # (rød)
        "button_style_background": "#333333",  # Tekstfarge for button style knapper
        "button_style_circle_background": "#a6c4be",  # bakgrunnsfarge på sirkel knapp med solbriller/øye
        "button_text": "#ffffff",  # Tekstfarge for knapper
        "input_background": "#d3c90d",  # Bakgrunnsfarge for inndatafelter (QLineEdit)
        "widget_background": "#f0e68c",  # Bakgrunnsfarge for widgets generelt
        "side_panel_background": "#b4a19e",  # Side panel background color
        "side_panel_border": "5px solid #333333",  # Side panel background color
        "label_text_color": "#ffffff",  # label tekst farge
        "label_background": "#444444",  # label bakgrunnsfarge
        # Farger for tabellstiler
        "header_background_table": "#3C3F41",  # Bakgrunnsfarge for tabellhoder
        "header_text_color_table": "#FFFFFF",  # Tekstfarge for tabellhoder
        "header_border_color_table": "#2E2E2E",  # Kantfarge for tabellhoder
        "row_background_table": "#73777C",  # Bakgrunnsfarge for tabellrader
        "row_text_color_table": "#FFFFFF",  # Tekstfarge for tabellrader
        "selected_row_background_table": "#4CAF50",  # Bakgrunnsfarge for valgte tabellrader
        "selected_row_text_color_table": "#FFFFFF",  # Tekstfarge for valgte tabellrader
    },
}

# Define button style template
BUTTON_STYLE = """
QPushButton {{
    background-color: {button_background};
    color: {button_text};
    border: none;
    padding: 12px 24px;
    border-radius: 5px;
    outline: none;
}}
QPushButton:hover {{
    background-color: {hover_background};
}}
"""

BUTTON_STYLE_CIRCLE = """
QToolButton {{
    background-color: {button_style_circle_background};
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
}}
"""

BUTTON_STYLE_STRENGTH = """
QPushButton {{
    background-color: {button_background};
    color: white;
    border: 1px solid gray;
    padding: 10px;
    border-radius: 5px;
    outline: none;
}}
QPushButton:checked {{
    background-color: {button_checked_background};
}}
"""

# Define line edit style template
LINE_EDIT_STYLE = """
QLineEdit {{
    background-color: {input_background};
    color: {text_color};
    border: 1px solid #ccc;
    padding: 5px;
}}
"""

# Define label style template
LABEL_STYLE = """
QLabel {{
    color: {label_text_color};
    background-color: {label_background};
    font-weight: bold;
    border-radius: 5px;  /* Legger til buede kanter */
    padding: 5px;  /* Legger til litt padding for bedre utseende */
}}
"""


PASSWORD_STYLE = """
QLineEdit {{
    background-color: {input_background};
    border: 1px solid #ccc;
    padding: 5px;
    min-height: 30px;  /* Sett en fast minimum høyde for å beholde konsistent utseende */
}}
"""


# Define combo box and spin box style template
COMBO_BOX_STYLE = """
QComboBox {{
    background-color: {input_background};
    color: {text_color};
    border: 1px solid #ccc;
    padding: 5px;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;
    border-left: 1px solid #ccc;
    background-color: {input_background};
}}

QComboBox::down-arrow {{
    border-top: 8px solid {arrow_color};  /* Juster størrelsen på pilen */
}}

QComboBox::down-arrow:on {{
    border-top: 8px solid gray;  /* Endre fargen på pilen når nedtrekksboksen er åpen */
}}

QComboBox QAbstractItemView {{
    background-color: {input_background};
    color: {text_color};
}}

QSpinBox {{
    background-color: {input_background};
    color: {text_color};
    border: 1px solid #ccc;
    padding: 5px;
}}
"""


# Define table style template
TABLE_STYLE = """
QHeaderView::section {{
    background-color: {header_background};  /* Bakgrunnsfarge for header */
    color: {header_text_color};  /* Tekstfarge for header */
    font-weight: bold;  /* Gjør teksten i header fet */
    padding: 5px;
    border: 1px solid {header_border_color};  /* Kantlinje rundt header */
}}

QTableWidget::item {{
    background-color: {row_background};  /* Bakgrunnsfarge for rader */
    color: {row_text_color};  /* Tekstfarge for rader */
    padding: 5px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: {selected_row_background};  /* Bakgrunnsfarge for valgte rader */
    color: {selected_row_text_color};  /* Tekstfarge for valgte rader */
}}
"""
