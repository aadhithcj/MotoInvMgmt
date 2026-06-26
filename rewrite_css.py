import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_dark = '''DARK_THEME_STYLE = """
QMainWindow, QWidget {
    background-color: #0B1121;
    color: #F1F5F9;
    font-family: 'Segoe UI Variable', 'Segoe UI', Roboto, sans-serif;
    font-size: 13px;
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
    gridline-color: transparent;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    selection-background-color: rgba(249, 115, 22, 0.15);
    selection-color: #F97316;
}
QTableWidget::item {
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding: 8px 12px;
}
QTableWidget::item:selected {
    background-color: rgba(249, 115, 22, 0.15);
}
QHeaderView::section {
    background-color: #172033;
    color: #94A3B8;
    padding: 10px 8px;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    font-weight: bold;
}
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
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
"""'''

new_light = '''LIGHT_THEME_STYLE = """
QMainWindow, QWidget {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: 'Segoe UI Variable', 'Segoe UI', Roboto, sans-serif;
    font-size: 13px;
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
    gridline-color: transparent;
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: 12px;
    selection-background-color: rgba(249, 115, 22, 0.1);
    selection-color: #EA580C;
}
QTableWidget::item {
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    padding: 8px 12px;
}
QTableWidget::item:selected {
    background-color: rgba(249, 115, 22, 0.1);
}
QHeaderView::section {
    background-color: #F8FAFC;
    color: #64748B;
    padding: 10px 8px;
    border: none;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    font-weight: bold;
}
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
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
"""'''

# Replace DARK_THEME_STYLE block
dark_pattern = re.compile(r'DARK_THEME_STYLE\s*=\s*\"\"\"[\s\S]*?\"\"\"', re.MULTILINE)
content = dark_pattern.sub(new_dark, content)

# Replace LIGHT_THEME_STYLE block
light_pattern = re.compile(r'LIGHT_THEME_STYLE\s*=\s*\"\"\"[\s\S]*?\"\"\"', re.MULTILINE)
content = light_pattern.sub(new_light, content)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated stylesheets in main.py")
