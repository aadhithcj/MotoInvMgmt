import sys
import os
import tempfile
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPalette, QColor, QPixmap, QPainter, QPolygon
from PyQt6.QtCore import Qt, QPoint
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
QLineEdit, QComboBox {
    background-color: #1E293B;
    color: #E2E8F0;
    border: 1px solid #475569;
    padding: 6px 10px;
    border-radius: 4px;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #F97316;
}
QSpinBox, QDoubleSpinBox {
    background-color: #1E293B;
    color: #E2E8F0;
    border: 1px solid #475569;
    padding: 6px 30px 6px 10px;
    border-radius: 4px;
    min-height: 20px;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #F97316;
}
QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 26px;
    height: 16px;
    border-left: 1px solid #475569;
    border-bottom: 1px solid #475569;
    background-color: #334155;
    border-top-right-radius: 4px;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
    background-color: #475569;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: url({up_arrow_url});
    width: 10px;
    height: 10px;
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 26px;
    height: 16px;
    border-left: 1px solid #475569;
    background-color: #334155;
    border-bottom-right-radius: 4px;
}
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #475569;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    image: url({down_arrow_url});
    width: 10px;
    height: 10px;
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
QLineEdit, QComboBox {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    padding: 6px 10px;
    border-radius: 4px;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #F97316;
}
QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    padding: 6px 30px 6px 10px;
    border-radius: 4px;
    min-height: 20px;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #F97316;
}
QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 26px;
    height: 16px;
    border-left: 1px solid #CBD5E1;
    border-bottom: 1px solid #CBD5E1;
    background-color: #E2E8F0;
    border-top-right-radius: 4px;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
    background-color: #CBD5E1;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: url({up_arrow_url_dark});
    width: 10px;
    height: 10px;
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 26px;
    height: 16px;
    border-left: 1px solid #CBD5E1;
    background-color: #E2E8F0;
    border-bottom-right-radius: 4px;
}
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #CBD5E1;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    image: url({down_arrow_url_dark});
    width: 10px;
    height: 10px;
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

def create_arrow_image(file_path, direction, color):
    pixmap = QPixmap(12, 12)
    pixmap.fill(QColor(0, 0, 0, 0))
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(color)
    painter.setBrush(color)
    
    if direction == "up":
        polygon = QPolygon([
            QPoint(6, 3),
            QPoint(2, 8),
            QPoint(10, 8)
        ])
    else:
        polygon = QPolygon([
            QPoint(6, 8),
            QPoint(2, 3),
            QPoint(10, 3)
        ])
        
    painter.drawPolygon(polygon)
    painter.end()
    pixmap.save(file_path, "PNG")

def generate_arrow_icons():
    temp_dir = tempfile.gettempdir()
    up_path = os.path.join(temp_dir, "gearfield_up_arrow.png").replace('\\', '/')
    down_path = os.path.join(temp_dir, "gearfield_down_arrow.png").replace('\\', '/')
    up_path_dark = os.path.join(temp_dir, "gearfield_up_arrow_dark.png").replace('\\', '/')
    down_path_dark = os.path.join(temp_dir, "gearfield_down_arrow_dark.png").replace('\\', '/')
    
    create_arrow_image(up_path, "up", QColor("#E2E8F0"))
    create_arrow_image(down_path, "down", QColor("#E2E8F0"))
    create_arrow_image(up_path_dark, "up", QColor("#0F172A"))
    create_arrow_image(down_path_dark, "down", QColor("#0F172A"))
    
    return up_path, down_path, up_path_dark, down_path_dark

def main():
    app = QApplication(sys.argv)
    
    # Generate spin box arrow icons dynamically
    up_path, down_path, up_path_dark, down_path_dark = generate_arrow_icons()
    
    global DARK_THEME_STYLE, LIGHT_THEME_STYLE
    DARK_THEME_STYLE = DARK_THEME_STYLE.replace("{up_arrow_url}", up_path).replace("{down_arrow_url}", down_path)
    LIGHT_THEME_STYLE = LIGHT_THEME_STYLE.replace("{up_arrow_url_dark}", up_path_dark).replace("{down_arrow_url_dark}", down_path_dark)

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
