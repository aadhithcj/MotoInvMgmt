import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTextEdit, QFormLayout, 
                             QMessageBox, QGroupBox, QScrollArea)
from database.models import get_setting, set_setting

class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)
        
        # Scroll Area for all settings contents
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(15)
        
        # Shop Details Group
        shop_group = QGroupBox("Shop Details")
        shop_layout = QFormLayout()
        
        self.shop_name = QLineEdit()
        self.shop_phone = QLineEdit()
        self.shop_email = QLineEdit()
        self.shop_gstin = QLineEdit()
        self.shop_state = QLineEdit()
        self.shop_address = QTextEdit()
        self.shop_address.setFixedHeight(60)
        
        shop_layout.addRow("Shop Name:", self.shop_name)
        shop_layout.addRow("Phone Number:", self.shop_phone)
        shop_layout.addRow("Email Address:", self.shop_email)
        shop_layout.addRow("GSTIN / UIN:", self.shop_gstin)
        shop_layout.addRow("State & State Code:", self.shop_state)
        shop_layout.addRow("Address:", self.shop_address)
        shop_group.setLayout(shop_layout)
        scroll_layout.addWidget(shop_group)
        
        # Bank Details Group
        bank_group = QGroupBox("Company's Bank Details")
        bank_layout = QFormLayout()
        
        self.bank_name = QLineEdit()
        self.bank_ac_no = QLineEdit()
        self.bank_branch = QLineEdit()
        self.bank_ifsc = QLineEdit()
        
        bank_layout.addRow("Bank Name:", self.bank_name)
        bank_layout.addRow("Account Number:", self.bank_ac_no)
        bank_layout.addRow("Branch Name:", self.bank_branch)
        bank_layout.addRow("IFSC Code:", self.bank_ifsc)
        bank_group.setLayout(bank_layout)
        scroll_layout.addWidget(bank_group)
        
        # Customer Bill Column Mapping Group
        mapping_group = QGroupBox("Customer Bill Column Mapping (JSON Format)")
        mapping_layout = QVBoxLayout()
        
        mapping_desc = QLabel("Edit keywords used to identify columns in Customer Bills. \nFormat: {\"column_type\": [\"keyword1\", \"keyword2\"]}")
        mapping_desc.setStyleSheet("color: #94A3B8;")
        mapping_layout.addWidget(mapping_desc)
        
        self.mapping_editor = QTextEdit()
        self.mapping_editor.setStyleSheet("font-family: Consolas, monospace;")
        self.mapping_editor.setFixedHeight(120)
        mapping_layout.addWidget(self.mapping_editor)
        
        mapping_group.setLayout(mapping_layout)
        scroll_layout.addWidget(mapping_group)
        
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        # Save Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("Save Settings")
        save_btn.setProperty("class", "Primary")
        save_btn.setMinimumWidth(150)
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)
        
        main_layout.addLayout(btn_layout)
        
    def load_data(self):
        self.shop_name.setText(get_setting('shop_name', ''))
        self.shop_phone.setText(get_setting('shop_phone', ''))
        self.shop_email.setText(get_setting('shop_email', ''))
        self.shop_gstin.setText(get_setting('shop_gstin', ''))
        self.shop_state.setText(get_setting('shop_state', ''))
        self.shop_address.setPlainText(get_setting('shop_address', ''))
        
        self.bank_name.setText(get_setting('bank_name', ''))
        self.bank_ac_no.setText(get_setting('bank_ac_no', ''))
        self.bank_branch.setText(get_setting('bank_branch', ''))
        self.bank_ifsc.setText(get_setting('bank_ifsc', ''))
        
        default_mapping = '{\n  "part_number": ["part no", "part number", "code", "item code"],\n  "part_name": ["description", "item", "name", "part name"],\n  "quantity": ["qty", "quantity", "units"],\n  "unit_price": ["price", "unit price", "rate"],\n  "total": ["total", "amount", "line total"]\n}'
        mapping_val = get_setting('customer_bill_mapping', default_mapping)
        
        try:
            parsed = json.loads(mapping_val)
            formatted = json.dumps(parsed, indent=4)
            self.mapping_editor.setPlainText(formatted)
        except:
            self.mapping_editor.setPlainText(mapping_val)
            
    def save_settings(self):
        set_setting('shop_name', self.shop_name.text().strip())
        set_setting('shop_phone', self.shop_phone.text().strip())
        set_setting('shop_email', self.shop_email.text().strip())
        set_setting('shop_gstin', self.shop_gstin.text().strip())
        set_setting('shop_state', self.shop_state.text().strip())
        set_setting('shop_address', self.shop_address.toPlainText().strip())
        
        set_setting('bank_name', self.bank_name.text().strip())
        set_setting('bank_ac_no', self.bank_ac_no.text().strip())
        set_setting('bank_branch', self.bank_branch.text().strip())
        set_setting('bank_ifsc', self.bank_ifsc.text().strip())
        
        # Validate JSON mapping
        mapping_text = self.mapping_editor.toPlainText().strip()
        try:
            json.loads(mapping_text) # test parse
            set_setting('customer_bill_mapping', mapping_text)
            QMessageBox.information(self, "Success", "Settings saved successfully.")
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"Could not save Column Mapping. Invalid JSON format:\n{str(e)}")

