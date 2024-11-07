from styles import (
    THEMES,
    BUTTON_STYLE,
    BUTTON_STYLE_CIRCLE,
    BUTTON_STYLE_STRENGTH,
    LABEL_STYLE,
    LINE_EDIT_STYLE,
    COMBO_BOX_STYLE,
    PASSWORD_STYLE,
    TABLE_STYLE,
)

from PySide2.QtWidgets import QComboBox, QSpinBox


class StyleManager:
    def __init__(self, theme_name="default"):
        self.theme = THEMES.get(theme_name, THEMES["default"])

    def apply_button_style(self, button):
        button.setStyleSheet(
            BUTTON_STYLE.format(
                button_background=self.theme["button_style_background"],
                button_text=self.theme["button_text"],
                hover_background=self.theme["button_hover_color"],
            )
        )

    def apply_button_style_1(self, button):
        button.setStyleSheet(
            BUTTON_STYLE.format(
                button_background=self.theme["button_style_background"],
                button_text=self.theme["button_text"],
                hover_background=self.theme["button_hover_color_1"],
            )
        )

    def apply_button_style_2(self, button):
        button.setStyleSheet(
            BUTTON_STYLE.format(
                button_background=self.theme["button_style_background"],
                button_text=self.theme["button_text"],
                hover_background=self.theme["button_hover_color_2"],
            )
        )

    def apply_button_style_circle(self, button):
        button.setStyleSheet(
            BUTTON_STYLE_CIRCLE.format(
                button_style_circle_background=self.theme[
                    "button_style_circle_background"
                ]
            )
        )

    def apply_button_style_strength_1(self, button):
        button.setStyleSheet(
            BUTTON_STYLE_STRENGTH.format(
                button_background=self.theme["button_mode_unchecked_1"],
                button_checked_background=self.theme["button_mode_checked_1"],
            )
        )

    def apply_button_style_strength_2(self, button):
        button.setStyleSheet(
            BUTTON_STYLE_STRENGTH.format(
                button_background=self.theme["button_mode_unchecked_2"],
                button_checked_background=self.theme["button_mode_checked_2"],
            )
        )

    def apply_button_style_strength_3(self, button):
        button.setStyleSheet(
            BUTTON_STYLE_STRENGTH.format(
                button_background=self.theme["button_mode_unchecked_3"],
                button_checked_background=self.theme["button_mode_checked_3"],
            )
        )

    def apply_line_edit_style(self, widget):
        if isinstance(widget, QComboBox) or isinstance(widget, QSpinBox):
            widget.setStyleSheet(
                COMBO_BOX_STYLE.format(
                    input_background=self.theme["input_background"],
                    text_color=self.theme["button_hover_color"],  # Use the correct key
                    arrow_color=self.theme["button_hover_color"],
                )
            )
        else:
            widget.setStyleSheet(
                LINE_EDIT_STYLE.format(
                    input_background=self.theme["input_background"],
                    text_color=self.theme["button_hover_color"],
                )
            )

    def apply_label_style(self, label):
        label.setStyleSheet(
            LABEL_STYLE.format(
                label_text_color=self.theme["label_text_color"],
                label_background=self.theme["label_background"],
            )
        )

    def apply_password_input_style(self, password_input):
        password_input.setStyleSheet(
            PASSWORD_STYLE.format(input_background=self.theme["input_background"])
        )

    def apply_central_widget_style(self, widget):
        widget.setStyleSheet(f"background-color: {self.theme['background']};")

    def apply_stack_style(self, stack_widget):
        stack_widget.setStyleSheet(
            f"background-color: {self.theme['stack_background']};"
        )

    def apply_side_panel_style(self, panel):
        panel.setStyleSheet(
            f"""
            background-color: {self.theme['side_panel_background']};
            border: {self.theme['side_panel_border']};
        """
        )

    def apply_table_style(self, table):
        table.setStyleSheet(
            TABLE_STYLE.format(
                header_background=self.theme["header_background_table"],
                header_text_color=self.theme["header_text_color_table"],
                header_border_color=self.theme["header_border_color_table"],
                row_background=self.theme["row_background_table"],
                row_text_color=self.theme["row_text_color_table"],
                selected_row_background=self.theme["selected_row_background_table"],
                selected_row_text_color=self.theme["selected_row_text_color_table"],
            )
        )
