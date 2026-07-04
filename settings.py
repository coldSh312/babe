"""
settings.py
===========

Application-wide constants and styling.

Keeping visual and configuration constants in one place makes it easy to
re-theme the application or change storage locations without touching
business logic or UI wiring code.
"""

from __future__ import annotations

import sys
from pathlib import Path

APP_NAME = "ניהול הגעת מטופלים"
ORG_NAME = "ClinicAttendanceApp"

# Checkmark symbol used to mark attendance in the table.
CHECK_MARK = "\u2714"  # ✔

# ----------------------------------------------------------------------
# Data storage location
# ----------------------------------------------------------------------
# When packaged with PyInstaller, we want the data file to live next to the
# executable (or in a user-writable app-data folder) rather than inside the
# temporary bundle. This helper resolves a sensible, persistent location.


def get_data_file_path() -> Path:
    """Return the path to the JSON data file used to persist app data.

    When running as a frozen PyInstaller executable, the file is stored
    next to the executable. Otherwise, it's stored next to this script.
    """
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).resolve().parent
    return base_dir / "clinic_data.json"


DATA_FILE = get_data_file_path()

# ----------------------------------------------------------------------
# Fonts & sizing
# ----------------------------------------------------------------------
FONT_FAMILY = "Segoe UI"
FONT_SIZE_NORMAL = 11
FONT_SIZE_LARGE = 14
FONT_SIZE_TITLE = 18

MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 750

# ----------------------------------------------------------------------
# Color palette (modern, clean, flat design)
# ----------------------------------------------------------------------
COLOR_BACKGROUND = "#F5F7FA"
COLOR_SURFACE = "#FFFFFF"
COLOR_PRIMARY = "#2F6FED"
COLOR_PRIMARY_HOVER = "#255BC4"
COLOR_PRIMARY_PRESSED = "#1E49A0"
COLOR_DANGER = "#E5484D"
COLOR_DANGER_HOVER = "#C93A3E"
COLOR_SUCCESS = "#2FB380"
COLOR_TEXT = "#1F2430"
COLOR_TEXT_MUTED = "#6B7280"
COLOR_BORDER = "#E1E5EB"
COLOR_TABLE_HEADER = "#EEF2FB"
COLOR_TABLE_ALT_ROW = "#FAFBFD"
COLOR_CHECK_CELL = "#E5F6EE"

STYLE_SHEET = f"""
QWidget {{
    background-color: {COLOR_BACKGROUND};
    color: {COLOR_TEXT};
    font-family: "{FONT_FAMILY}";
    font-size: {FONT_SIZE_NORMAL}pt;
}}

QMainWindow {{
    background-color: {COLOR_BACKGROUND};
}}

/* ---------------- Panels ---------------- */
QFrame#sidePanel {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 10px;
}}

QLabel#sectionTitle {{
    font-size: {FONT_SIZE_LARGE}pt;
    font-weight: 600;
    color: {COLOR_TEXT};
    padding-bottom: 4px;
}}

QLabel#appTitle {{
    font-size: {FONT_SIZE_TITLE}pt;
    font-weight: 700;
    color: {COLOR_TEXT};
}}

QLabel#summaryLabel {{
    font-size: {FONT_SIZE_LARGE}pt;
    font-weight: 600;
    color: {COLOR_TEXT};
}}

QLabel#incomeLabel {{
    font-size: {FONT_SIZE_LARGE + 2}pt;
    font-weight: 700;
    color: {COLOR_SUCCESS};
}}

QLabel#hint {{
    color: {COLOR_TEXT_MUTED};
    font-size: {FONT_SIZE_NORMAL - 1}pt;
}}

/* ---------------- Buttons ---------------- */
QPushButton {{
    background-color: {COLOR_PRIMARY};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 600;
    font-size: {FONT_SIZE_NORMAL}pt;
}}

QPushButton:hover {{
    background-color: {COLOR_PRIMARY_HOVER};
}}

QPushButton:pressed {{
    background-color: {COLOR_PRIMARY_PRESSED};
}}

QPushButton:disabled {{
    background-color: #B7C4E0;
}}

QPushButton#dangerButton {{
    background-color: {COLOR_DANGER};
}}

QPushButton#dangerButton:hover {{
    background-color: {COLOR_DANGER_HOVER};
}}

QPushButton#secondaryButton {{
    background-color: {COLOR_SURFACE};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BORDER};
}}

QPushButton#secondaryButton:hover {{
    background-color: {COLOR_TABLE_HEADER};
}}

/* ---------------- Inputs ---------------- */
QLineEdit, QDoubleSpinBox {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    padding: 8px 10px;
    selection-background-color: {COLOR_PRIMARY};
}}

QLineEdit:focus, QDoubleSpinBox:focus {{
    border: 1px solid {COLOR_PRIMARY};
}}

/* ---------------- List widgets ---------------- */
QListWidget {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    padding: 4px;
    outline: none;
}}

QListWidget::item {{
    padding: 8px 6px;
    border-radius: 6px;
}}

QListWidget::item:selected {{
    background-color: {COLOR_TABLE_HEADER};
    color: {COLOR_TEXT};
}}

QListWidget::item:hover {{
    background-color: {COLOR_TABLE_HEADER};
}}

/* ---------------- Table ---------------- */
QTableWidget {{
    background-color: {COLOR_SURFACE};
    gridline-color: {COLOR_BORDER};
    border: 1px solid {COLOR_BORDER};
    border-radius: 10px;
    selection-background-color: transparent;
}}

QTableWidget::item {{
    padding: 4px;
}}

QHeaderView::section {{
    background-color: {COLOR_TABLE_HEADER};
    color: {COLOR_TEXT};
    padding: 10px 6px;
    border: none;
    border-bottom: 2px solid {COLOR_BORDER};
    border-left: 1px solid {COLOR_BORDER};
    font-weight: 600;
}}

QTableCornerButton::section {{
    background-color: {COLOR_TABLE_HEADER};
    border: none;
}}

QScrollBar:vertical, QScrollBar:horizontal {{
    background: {COLOR_BACKGROUND};
    border: none;
    border-radius: 6px;
}}

QScrollBar::handle {{
    background: #C7CEDB;
    border-radius: 6px;
    min-height: 20px;
    min-width: 20px;
}}

QScrollBar::handle:hover {{
    background: #A9B3C6;
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0px;
    width: 0px;
}}
"""
