"""Dark Theme styling and QSS definitions for LumieTL Desktop."""

from core.config import COLORS

DARK_THEME_QSS = f"""
/* Global Reset & Typography */
QWidget {{
    background-color: {COLORS["bg_base"]};
    color: {COLORS["text_primary"]};
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
    selection-background-color: {COLORS["accent"]};
    selection-color: #FFFFFF;
}}

/* Main Window & Containers */
QMainWindow {{
    background-color: {COLORS["bg_base"]};
}}

QFrame#sidebar {{
    background-color: {COLORS["bg_surface"]};
    border-right: 1px solid {COLORS["border"]};
}}

QFrame#content_area {{
    background-color: {COLORS["bg_base"]};
}}

QFrame#card {{
    background-color: {COLORS["bg_surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
}}

/* Labels & Headings */
QLabel {{
    background: transparent;
    color: {COLORS["text_primary"]};
}}

QLabel#heading {{
    font-size: 18px;
    font-weight: bold;
    color: {COLORS["text_primary"]};
}}

QLabel#subheading {{
    font-size: 13px;
    color: {COLORS["text_secondary"]};
}}

/* Buttons */
QPushButton {{
    background-color: {COLORS["bg_elevated"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {COLORS["border"]};
    border-color: #3A3A42;
}}

QPushButton:pressed {{
    background-color: {COLORS["bg_surface"]};
}}

QPushButton:disabled {{
    background-color: {COLORS["bg_surface"]};
    color: {COLORS["text_secondary"]};
    border-color: {COLORS["border"]};
}}

QPushButton#primary_button {{
    background-color: {COLORS["accent"]};
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}}

QPushButton#primary_button:hover {{
    background-color: #7D9CF8;
}}

QPushButton#primary_button:pressed {{
    background-color: #5B7CE0;
}}

QPushButton#sidebar_button {{
    background-color: transparent;
    border: none;
    border-radius: 6px;
    color: {COLORS["text_secondary"]};
    text-align: left;
    padding: 10px 14px;
    font-weight: 500;
}}

QPushButton#sidebar_button:hover {{
    background-color: {COLORS["bg_elevated"]};
    color: {COLORS["text_primary"]};
}}

QPushButton#sidebar_button:checked {{
    background-color: {COLORS["bg_elevated"]};
    color: {COLORS["accent"]};
    font-weight: 600;
}}

/* Inputs & Combos */
QLineEdit, QComboBox, QSpinBox {{
    background-color: {COLORS["bg_elevated"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 6px 10px;
}}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border: 1px solid {COLORS["accent"]};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS["bg_surface"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    selection-background-color: {COLORS["accent"]};
    selection-color: #FFFFFF;
}}

/* Table Widget */
QTableWidget {{
    background-color: {COLORS["bg_surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    gridline-color: {COLORS["border"]};
}}

QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {COLORS["border"]};
}}

QTableWidget::item:selected {{
    background-color: {COLORS["bg_elevated"]};
    color: {COLORS["text_primary"]};
}}

QHeaderView::section {{
    background-color: {COLORS["bg_base"]};
    color: {COLORS["text_secondary"]};
    padding: 8px;
    border: none;
    border-bottom: 1px solid {COLORS["border"]};
    font-weight: 600;
}}

/* Progress Bar */
QProgressBar {{
    background-color: {COLORS["bg_elevated"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 4px;
    text-align: center;
    color: {COLORS["text_primary"]};
    height: 14px;
}}

QProgressBar::chunk {{
    background-color: {COLORS["accent"]};
    border-radius: 3px;
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: {COLORS["bg_base"]};
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {COLORS["border"]};
    min-height: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS["text_secondary"]};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* Dialogs */
QDialog {{
    background-color: {COLORS["bg_surface"]};
}}
"""
