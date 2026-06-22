from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QLineEdit, QDialog, QFormLayout, QMessageBox, QTextEdit)
from database.models import get_all_suppliers, add_supplier, update_supplier, delete_supplier, get_supplier_by_name

class SupplierDialog(QDialog):
    def __init__(self, parent=None, supplier_data=None):
        super().__init__(parent)
        self.supplier_data = supplier_data
        self.setWindowTitle("Add Supplier" if not supplier_data else "Edit Supplier")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QTextEdit()
        self.address_input.setFixedHeight(80)
        
        if self.supplier_data:
            self.name_input.setText(self.supplier_data.get('name', ''))
            self.phone_input.setText(self.supplier_data.get('phone', ''))
            self.address_input.setPlainText(self.supplier_data.get('address', ''))
            
        layout.addRow("Name:", self.name_input)
        layout.addRow("Phone:", self.phone_input)
        layout.addRow("Address:", self.address_input)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setProperty("class", "Primary")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addRow(btn_layout)

    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'address': self.address_input.toPlainText().strip()
        }

class SuppliersScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Suppliers")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        add_btn = QPushButton("+ Add Supplier")
        add_btn.setProperty("class", "Primary")
        add_btn.clicked.connect(self.add_supplier)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Address"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.edit_supplier)
        
        layout.addWidget(self.table)
        
        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        
        edit_btn = QPushButton("Edit Selected")
        edit_btn.clicked.connect(self.edit_supplier)
        
        delete_btn = QPushButton("Delete Selected")
        delete_btn.setStyleSheet("background-color: #EF4444; color: white;")
        delete_btn.clicked.connect(self.delete_supplier)
        
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        layout.addLayout(actions_layout)

    def load_data(self):
        suppliers = get_all_suppliers()
        self.table.setRowCount(0)
        for row, supplier in enumerate(suppliers):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(supplier['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(supplier['name']))
            self.table.setItem(row, 2, QTableWidgetItem(supplier['phone'] or ""))
            self.table.setItem(row, 3, QTableWidgetItem(supplier['address'] or ""))

    def get_selected_id(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        return int(self.table.item(row, 0).text())

    def add_supplier(self):
        dialog = SupplierDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Error", "Supplier Name is required.")
                return
            try:
                add_supplier(data)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def edit_supplier(self, item=None):
        supplier_id = self.get_selected_id()
        if not supplier_id:
            QMessageBox.information(self, "Select Supplier", "Please select a supplier to edit.")
            return
            
        row = self.table.currentRow()
        data = {
            'id': supplier_id,
            'name': self.table.item(row, 1).text(),
            'phone': self.table.item(row, 2).text(),
            'address': self.table.item(row, 3).text()
        }
        
        dialog = SupplierDialog(self, data)
        if dialog.exec():
            new_data = dialog.get_data()
            if not new_data['name']:
                QMessageBox.warning(self, "Error", "Supplier Name is required.")
                return
            try:
                update_supplier(supplier_id, new_data)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def delete_supplier(self):
        supplier_id = self.get_selected_id()
        if not supplier_id:
            QMessageBox.information(self, "Select Supplier", "Please select a supplier to delete.")
            return
            
        reply = QMessageBox.question(self, "Confirm Delete", 
                                     "Are you sure you want to delete this supplier?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                                     
        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_supplier(supplier_id)
                self.load_data()
            except ValueError as e:
                QMessageBox.warning(self, "Cannot Delete", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Database Error", str(e))
