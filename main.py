import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPalette, QColor
from PyQt6.QtCore import Qt
from database.connection import init_db
from database.models import get_setting
from ui.main_window import MainWindow

DARK_THEME_STYLE = """
QMainWindow, QWidget {
    background-color: #0F172A;
    color: #E2E8F0;
    font-family: 'Segoe UI', Roboto, sans-serif;
    font-size: 13px;
}
QFrame#Sidebar {
    background-color: #1E293B;
    border-right: 1px solid #334155;
}
QPushButton {
    background-color: #334155;
    color: #F8FAFC;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #475569;
}
QPushButton.Primary {
    background-color: #F97316; /* Orange Tint */
    color: white;
    font-weight: bold;
}
QPushButton.Primary:hover {
    background-color: #EA580C;
}
QPushButton.Primary:disabled {
    background-color: #94A3B8;
    color: #E2E8F0;
}
QPushButton.NavButton {
    text-align: left;
    padding: 12px 20px;
    background-color: transparent;
    border-radius: 0px;
}
QPushButton.NavButton:hover {
    background-color: #334155;
}
QPushButton.NavButton:checked {
    background-color: #F97316;
    color: white;
    font-weight: bold;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #1E293B;
    color: #E2E8F0;
    border: 1px solid #475569;
    padding: 6px 10px;
    border-radius: 4px;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #F97316;
}
QTableWidget, QTableView {
    background-color: #1E293B;
    color: #E2E8F0;
    gridline-color: #334155;
    border: 1px solid #334155;
    border-radius: 4px;
}
QHeaderView::section {
    background-color: #0F172A;
    color: #94A3B8;
    padding: 6px;
    border: 1px solid #334155;
    font-weight: bold;
}
QScrollBar:vertical {
    border: none;
    background: #0F172A;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #475569;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
QFrame#StatCard {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
}
QLabel#StatCardTitle {
    color: #94A3B8;
    font-size: 14px;
    border: none;
    background-color: transparent;
}
QLabel#StatCardValue {
    font-size: 24px;
    font-weight: bold;
    border: none;
    background-color: transparent;
}
"""

LIGHT_THEME_STYLE = """
QMainWindow, QWidget {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: 'Segoe UI', Roboto, sans-serif;
    font-size: 13px;
}
QFrame#Sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}
QPushButton {
    background-color: #E2E8F0;
    color: #0F172A;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #CBD5E1;
}
QPushButton.Primary {
    background-color: #F97316; /* Orange Tint */
    color: white;
    font-weight: bold;
}
QPushButton.Primary:hover {
    background-color: #EA580C;
}
QPushButton.Primary:disabled {
    background-color: #94A3B8;
    color: white;
}
QPushButton.NavButton {
    text-align: left;
    padding: 12px 20px;
    background-color: transparent;
    border-radius: 0px;
}
QPushButton.NavButton:hover {
    background-color: #F1F5F9;
}
QPushButton.NavButton:checked {
    background-color: #F97316;
    color: white;
    font-weight: bold;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    padding: 6px 10px;
    border-radius: 4px;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #F97316;
}
QTableWidget, QTableView {
    background-color: #FFFFFF;
    color: #0F172A;
    gridline-color: #E2E8F0;
    border: 1px solid #E2E8F0;
    border-radius: 4px;
}
QHeaderView::section {
    background-color: #F8FAFC;
    color: #475569;
    padding: 6px;
    border: 1px solid #E2E8F0;
    font-weight: bold;
}
QScrollBar:vertical {
    border: none;
    background: #F8FAFC;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
QFrame#StatCard {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
}
QLabel#StatCardTitle {
    color: #64748B;
    font-size: 14px;
    border: none;
    background-color: transparent;
}
QLabel#StatCardValue {
    font-size: 24px;
    font-weight: bold;
    border: none;
    background-color: transparent;
}
"""

def main():
    app = QApplication(sys.argv)
    
    # Force high DPI scaling if supported
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    # Initialize Database
    init_db()

    # Apply Theme
    theme = get_setting('theme', 'dark')
    if theme == 'light':
        app.setStyleSheet(LIGHT_THEME_STYLE)
    else:
        app.setStyleSheet(DARK_THEME_STYLE)

    window = MainWindow(app, DARK_THEME_STYLE, LIGHT_THEME_STYLE)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
