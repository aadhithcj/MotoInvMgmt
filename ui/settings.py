import json
import shutil
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTextEdit, QFormLayout, 
                             QMessageBox, QGroupBox, QScrollArea, QFileDialog)
from database.models import get_setting, set_setting
from .toast import ToastNotification

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
        
        # Logo Selection Row
        self.shop_logo_path = QLineEdit()
        self.shop_logo_path.setReadOnly(True)
        self.choose_logo_btn = QPushButton("Choose Logo")
        self.choose_logo_btn.clicked.connect(self.choose_logo)
        self.remove_logo_btn = QPushButton("Remove Logo")
        self.remove_logo_btn.setStyleSheet("background-color: #EF4444; color: white;")
        self.remove_logo_btn.clicked.connect(self.remove_logo)
        
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.shop_logo_path)
        logo_layout.addWidget(self.choose_logo_btn)
        logo_layout.addWidget(self.remove_logo_btn)
        
        shop_layout.addRow("Shop Name:", self.shop_name)
        shop_layout.addRow("Phone Number:", self.shop_phone)
        shop_layout.addRow("Email Address:", self.shop_email)
        shop_layout.addRow("GSTIN / UIN:", self.shop_gstin)
        shop_layout.addRow("State & State Code:", self.shop_state)
        shop_layout.addRow("Address:", self.shop_address)
        shop_layout.addRow("Shop Logo:", logo_layout)
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
        

        # AI Integration Group
        ai_group = QGroupBox("AI Integration")
        ai_layout = QFormLayout()
        
        self.gemini_api_key = QLineEdit()
        self.gemini_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_api_key.setPlaceholderText("Paste your free Gemini API Key here")
        
        ai_layout.addRow("Gemini API Key:", self.gemini_api_key)
        ai_group.setLayout(ai_layout)
        scroll_layout.addWidget(ai_group)
        
        # Database Backup & Restore Group
        db_group = QGroupBox("Database Backup & Restore")
        db_layout = QHBoxLayout()
        
        backup_btn = QPushButton("Backup Database")
        backup_btn.clicked.connect(self.backup_database)
        
        restore_btn = QPushButton("Restore Database")
        restore_btn.clicked.connect(self.restore_database)
        
        db_layout.addWidget(backup_btn)
        db_layout.addWidget(restore_btn)
        db_group.setLayout(db_layout)
        scroll_layout.addWidget(db_group)
        
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
        self.shop_logo_path.setText(get_setting('shop_logo_path', ''))
        
        self.bank_name.setText(get_setting('bank_name', ''))
        self.bank_ac_no.setText(get_setting('bank_ac_no', ''))
        self.bank_branch.setText(get_setting('bank_branch', ''))
        self.bank_ifsc.setText(get_setting('bank_ifsc', ''))
        
        self.gemini_api_key.setText(get_setting('gemini_api_key', ''))
            
    def save_settings(self):
        set_setting('shop_name', self.shop_name.text().strip())
        set_setting('shop_phone', self.shop_phone.text().strip())
        set_setting('shop_email', self.shop_email.text().strip())
        set_setting('shop_gstin', self.shop_gstin.text().strip())
        set_setting('shop_state', self.shop_state.text().strip())
        set_setting('shop_address', self.shop_address.toPlainText().strip())
        set_setting('shop_logo_path', self.shop_logo_path.text().strip())
        
        set_setting('bank_name', self.bank_name.text().strip())
        set_setting('bank_ac_no', self.bank_ac_no.text().strip())
        set_setting('bank_branch', self.bank_branch.text().strip())
        set_setting('bank_ifsc', self.bank_ifsc.text().strip())
        
        set_setting('gemini_api_key', self.gemini_api_key.text().strip())
        ToastNotification.show_toast(self.window(), "Settings saved successfully.")

    def choose_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Shop Logo", "", "Image Files (*.png *.jpg *.jpeg)")
        if path:
            self.shop_logo_path.setText(path)
            
    def remove_logo(self):
        self.shop_logo_path.setText("")
        
    def backup_database(self):
        default_name = "gearfield_backup.db"
        path, _ = QFileDialog.getSaveFileName(self, "Backup Database", default_name, "Database Files (*.db)")
        if not path:
            return
            
        try:
            from database.connection import DB_NAME
            shutil.copy(DB_NAME, path)
            QMessageBox.information(self, "Backup Success", f"Database backed up successfully to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Failed", f"Could not backup database:\n{str(e)}")
            
    def restore_database(self):
        reply = QMessageBox.question(self, "Restore Database", 
                                     "Restoring a database will overwrite your current data. Are you sure you want to proceed?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
            
        path, _ = QFileDialog.getOpenFileName(self, "Select Database Backup", "", "Database Files (*.db)")
        if not path:
            return
            
        try:
            from database.connection import DB_NAME
            shutil.copy(path, DB_NAME)
            QMessageBox.information(self, "Restore Success", "Database restored successfully. Please restart the application to apply all changes.")
        except Exception as e:
            QMessageBox.critical(self, "Restore Failed", f"Could not restore database:\n{str(e)}")

