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
    background-color: #0B1121;
    color: #F1F5F9;
    font-family: 'Segoe UI Variable', 'Segoe UI', Roboto, sans-serif;
    font-size: 13px;
}
QLabel {
    background-color: transparent;
}
QFrame#Sidebar {
    background-color: #172033;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}
QPushButton {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 8px 16px;
    border-radius: 8px;
}
QPushButton:hover {
    background-color: #334155;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
QPushButton.Primary {
    background-color: #F97316; 
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 8px;
}
QPushButton.Primary:hover {
    background-color: #EA580C;
}
QPushButton.Primary:disabled {
    background-color: #475569;
    color: #94A3B8;
}
QPushButton.NavButton {
    text-align: left;
    padding: 12px 20px;
    background-color: transparent;
    border-radius: 0px;
    border: none;
}
QPushButton.NavButton:hover {
    background-color: rgba(255, 255, 255, 0.05);
}
QPushButton.NavButton:checked {
    background-color: rgba(249, 115, 22, 0.15);
    color: #F97316;
    font-weight: bold;
    border-right: 4px solid #F97316;
}
QLineEdit, QComboBox {
    background-color: #172033;
    color: #F1F5F9;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 8px 12px;
    border-radius: 8px;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #F97316;
    background-color: #0B1121;
}
QSpinBox, QDoubleSpinBox {
    background-color: #172033;
    color: #F1F5F9;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 2px 20px 2px 5px;
    border-radius: 8px;
    min-height: 24px;
    qproperty-alignment: AlignCenter;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #F97316;
    background-color: #0B1121;
}
QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    height: 12px;
    border-left: 1px solid rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    background-color: #1E293B;
    border-top-right-radius: 8px;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
    background-color: #334155;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: url({up_arrow_url});
    width: 10px;
    height: 10px;
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    height: 12px;
    border-left: 1px solid rgba(255, 255, 255, 0.05);
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    background-color: #1E293B;
    border-bottom-right-radius: 8px;
}
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #334155;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    image: url({down_arrow_url});
    width: 10px;
    height: 10px;
}
QTableWidget, QTableView {
    background-color: #0B1121;
    color: #E2E8F0;
    gridline-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    selection-background-color: rgba(249, 115, 22, 0.15);
    selection-color: #F97316;
}
QTableWidget::item {
    padding: 4px 12px;
}
QTableWidget::item:selected {
    background-color: rgba(249, 115, 22, 0.15);
}
QHeaderView::section {
    background-color: #172033;
    color: #94A3B8;
    padding: 10px 24px 10px 8px;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    font-weight: bold;
}
QHeaderView::section:hover {
    background-color: rgba(255, 255, 255, 0.05);
}
QHeaderView::up-arrow {
    image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHdpZHRoPScxMicgaGVpZ2h0PScxMicgdmlld0JveD0nMCAwIDI0IDI0JyBmaWxsPSdub25lJyBzdHJva2U9JyNGOTczMTYnIHN0cm9rZS13aWR0aD0nMycgc3Ryb2tlLWxpbmVjYXA9J3JvdW5kJyBzdHJva2UtbGluZWpvaW49J3JvdW5kJz48cGF0aCBkPSdNMTggMTVsLTYtNi02IDYnLz48L3N2Zz4=");
    subcontrol-position: right center;
    width: 12px;
    height: 12px;
}
QHeaderView::down-arrow {
    image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHdpZHRoPScxMicgaGVpZ2h0PScxMicgdmlld0JveD0nMCAwIDI0IDI0JyBmaWxsPSdub25lJyBzdHJva2U9JyNGOTczMTYnIHN0cm9rZS13aWR0aD0nMycgc3Ryb2tlLWxpbmVjYXA9J3JvdW5kJyBzdHJva2UtbGluZWpvaW49J3JvdW5kJz48cGF0aCBkPSdNNiA5bDYgNiA2LTYnLz48L3N2Zz4=");
    subcontrol-position: right center;
    width: 12px;
    height: 12px;
}
QFrame#DialogContainer {
    background-color: #1E293B;
    border-radius: 12px;
    border: 1px solid #334155;
}
QLabel#DialogTitle {
    font-size: 18px;
    font-weight: bold;
    color: #F8FAFC;
    background: transparent;
    border: none;
}
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 5px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #334155;
    min-height: 30px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #475569;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}
QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 8px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: #334155;
    min-width: 30px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #475569;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
    width: 0px;
}
QFrame#StatCard {
    background-color: #172033;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
}
QLabel#StatCardTitle {
    color: #94A3B8;
    font-size: 13px;
    border: none;
    background-color: transparent;
}
QLabel#StatCardValue {
    font-size: 28px;
    font-weight: bold;
    color: #F8FAFC;
    border: none;
    background-color: transparent;
}

QGroupBox {
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    margin-top: 18px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    color: #94A3B8;
}
"""

LIGHT_THEME_STYLE = """
QMainWindow, QWidget {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: 'Segoe UI Variable', 'Segoe UI', Roboto, sans-serif;
    font-size: 13px;
}
QLabel {
    background-color: transparent;
}
QFrame#Sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid rgba(0, 0, 0, 0.05);
}
QPushButton {
    background-color: #F1F5F9;
    color: #0F172A;
    border: 1px solid rgba(0, 0, 0, 0.05);
    padding: 8px 16px;
    border-radius: 8px;
}
QPushButton:hover {
    background-color: #E2E8F0;
    border: 1px solid rgba(0, 0, 0, 0.1);
}
QPushButton.Primary {
    background-color: #F97316; 
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 8px;
}
QPushButton.Primary:hover {
    background-color: #EA580C;
}
QPushButton.Primary:disabled {
    background-color: #CBD5E1;
    color: #F8FAFC;
}
QPushButton.NavButton {
    text-align: left;
    padding: 12px 20px;
    background-color: transparent;
    border-radius: 0px;
    border: none;
}
QPushButton.NavButton:hover {
    background-color: rgba(0, 0, 0, 0.03);
}
QPushButton.NavButton:checked {
    background-color: rgba(249, 115, 22, 0.1);
    color: #EA580C;
    font-weight: bold;
    border-right: 4px solid #F97316;
}
QLineEdit, QComboBox {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid rgba(0, 0, 0, 0.1);
    padding: 8px 12px;
    border-radius: 8px;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #F97316;
    background-color: #FFFFFF;
}
QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid rgba(0, 0, 0, 0.1);
    padding: 2px 20px 2px 5px;
    border-radius: 8px;
    min-height: 24px;
    qproperty-alignment: AlignCenter;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #F97316;
}
QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    height: 12px;
    border-left: 1px solid rgba(0, 0, 0, 0.05);
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    background-color: #F1F5F9;
    border-top-right-radius: 8px;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
    background-color: #E2E8F0;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: url({up_arrow_url});
    width: 10px;
    height: 10px;
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    height: 12px;
    border-left: 1px solid rgba(0, 0, 0, 0.05);
    border-top: 1px solid rgba(0, 0, 0, 0.05);
    background-color: #F1F5F9;
    border-bottom-right-radius: 8px;
}
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #E2E8F0;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    image: url({down_arrow_url});
    width: 10px;
    height: 10px;
}
QTableWidget, QTableView {
    background-color: #FFFFFF;
    color: #334155;
    gridline-color: rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: 12px;
    selection-background-color: rgba(249, 115, 22, 0.1);
    selection-color: #EA580C;
}
QTableWidget::item {
    padding: 4px 12px;
}
QTableWidget::item:selected {
    background-color: rgba(249, 115, 22, 0.1);
}
QHeaderView::section {
    background-color: #F8FAFC;
    color: #64748B;
    padding: 10px 24px 10px 8px;
    border: none;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    font-weight: bold;
}
QHeaderView::section:hover {
    background-color: rgba(0, 0, 0, 0.05);
}
QHeaderView::up-arrow {
    image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHdpZHRoPScxMicgaGVpZ2h0PScxMicgdmlld0JveD0nMCAwIDI0IDI0JyBmaWxsPSdub25lJyBzdHJva2U9JyNGOTczMTYnIHN0cm9rZS13aWR0aD0nMycgc3Ryb2tlLWxpbmVjYXA9J3JvdW5kJyBzdHJva2UtbGluZWpvaW49J3JvdW5kJz48cGF0aCBkPSdNMTggMTVsLTYtNi02IDYnLz48L3N2Zz4=");
    subcontrol-position: right center;
    width: 12px;
    height: 12px;
}
QHeaderView::down-arrow {
    image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHdpZHRoPScxMicgaGVpZ2h0PScxMicgdmlld0JveD0nMCAwIDI0IDI0JyBmaWxsPSdub25lJyBzdHJva2U9JyNGOTczMTYnIHN0cm9rZS13aWR0aD0nMycgc3Ryb2tlLWxpbmVjYXA9J3JvdW5kJyBzdHJva2UtbGluZWpvaW49J3JvdW5kJz48cGF0aCBkPSdNNiA5bDYgNiA2LTYnLz48L3N2Zz4=");
    subcontrol-position: right center;
    width: 12px;
    height: 12px;
}
QFrame#DialogContainer {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
}
QLabel#DialogTitle {
    font-size: 18px;
    font-weight: bold;
    color: #0F172A;
    background: transparent;
    border: none;
}
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 5px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 30px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}
QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 8px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: #CBD5E1;
    min-width: 30px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #94A3B8;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
    width: 0px;
}
QFrame#StatCard {
    background-color: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: 12px;
}
QLabel#StatCardTitle {
    color: #64748B;
    font-size: 13px;
    border: none;
    background-color: transparent;
}
QLabel#StatCardValue {
    font-size: 28px;
    font-weight: bold;
    color: #0F172A;
    border: none;
    background-color: transparent;
}

QGroupBox {
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: 8px;
    margin-top: 18px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    color: #64748B;
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
