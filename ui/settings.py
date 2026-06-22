import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTextEdit, QFormLayout, 
                             QMessageBox, QGroupBox)
from database.models import get_setting, set_setting

class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Shop Details Group
        shop_group = QGroupBox("Shop Details")
        shop_layout = QFormLayout()
        
        self.shop_name = QLineEdit()
        self.shop_phone = QLineEdit()
        self.shop_address = QTextEdit()
        self.shop_address.setFixedHeight(80)
        
        shop_layout.addRow("Shop Name:", self.shop_name)
        shop_layout.addRow("Phone Number:", self.shop_phone)
        shop_layout.addRow("Address:", self.shop_address)
        shop_group.setLayout(shop_layout)
        layout.addWidget(shop_group)
        
        # Customer Bill Column Mapping Group
        mapping_group = QGroupBox("Customer Bill Column Mapping (JSON Format)")
        mapping_layout = QVBoxLayout()
        
        mapping_desc = QLabel("Edit keywords used to identify columns in Customer Bills. \nFormat: {\"column_type\": [\"keyword1\", \"keyword2\"]}")
        mapping_desc.setStyleSheet("color: #94A3B8;")
        mapping_layout.addWidget(mapping_desc)
        
        self.mapping_editor = QTextEdit()
        self.mapping_editor.setStyleSheet("font-family: Consolas, monospace;")
        mapping_layout.addWidget(self.mapping_editor)
        
        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)
        
        # Save Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("Save Settings")
        save_btn.setProperty("class", "Primary")
        save_btn.setMinimumWidth(150)
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)

    def load_data(self):
        self.shop_name.setText(get_setting('shop_name', ''))
        self.shop_phone.setText(get_setting('shop_phone', ''))
        self.shop_address.setPlainText(get_setting('shop_address', ''))
        
        default_mapping = '{\n  "part_number": ["part no", "part number", "code", "item code"],\n  "part_name": ["description", "item", "name", "part name"],\n  "quantity": ["qty", "quantity", "units"],\n  "unit_price": ["price", "unit price", "rate"],\n  "total": ["total", "amount", "line total"]\n}'
        mapping_val = get_setting('customer_bill_mapping', default_mapping)
        
        # Try to format JSON nicely
        try:
            parsed = json.loads(mapping_val)
            formatted = json.dumps(parsed, indent=4)
            self.mapping_editor.setPlainText(formatted)
        except:
            self.mapping_editor.setPlainText(mapping_val)

    def save_settings(self):
        set_setting('shop_name', self.shop_name.text().strip())
        set_setting('shop_phone', self.shop_phone.text().strip())
        set_setting('shop_address', self.shop_address.toPlainText().strip())
        
        # Validate JSON mapping
        mapping_text = self.mapping_editor.toPlainText().strip()
        try:
            json.loads(mapping_text) # test parse
            set_setting('customer_bill_mapping', mapping_text)
            QMessageBox.information(self, "Success", "Settings saved successfully.")
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"Could not save Column Mapping. Invalid JSON format:\n{str(e)}")
