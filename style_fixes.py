import re

# 1. Update settings.py
with open('ui/settings.py', 'r', encoding='utf-8') as f:
    settings_content = f.read()
settings_content = settings_content.replace(
    'scroll_layout.setContentsMargins(0, 0, 0, 0)',
    'scroll_layout.setContentsMargins(0, 0, 15, 0)'
)
with open('ui/settings.py', 'w', encoding='utf-8') as f:
    f.write(settings_content)

# 2. Update main.py
with open('main.py', 'r', encoding='utf-8') as f:
    main_content = f.read()

# Make scrollbar narrower
main_content = main_content.replace('width: 8px;', 'width: 5px;')

# Add QGroupBox to dark theme
dark_groupbox = """
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

# Add QGroupBox to light theme
light_groupbox = """
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

main_content = main_content.replace('QLabel#StatCardValue {\n    font-size: 28px;\n    font-weight: bold;\n    color: #F8FAFC;\n    border: none;\n    background-color: transparent;\n}\n"""', 'QLabel#StatCardValue {\n    font-size: 28px;\n    font-weight: bold;\n    color: #F8FAFC;\n    border: none;\n    background-color: transparent;\n}\n' + dark_groupbox + '"""')

main_content = main_content.replace('QLabel#StatCardValue {\n    font-size: 28px;\n    font-weight: bold;\n    color: #0F172A;\n    border: none;\n    background-color: transparent;\n}\n"""', 'QLabel#StatCardValue {\n    font-size: 28px;\n    font-weight: bold;\n    color: #0F172A;\n    border: none;\n    background-color: transparent;\n}\n' + light_groupbox + '"""')

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(main_content)

print("Applied groupbox styling and margin fixes")
