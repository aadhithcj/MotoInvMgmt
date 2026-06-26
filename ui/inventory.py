from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QLineEdit, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from .toast import ToastNotification
from database.models import get_all_parts, search_parts, add_part, update_part, delete_part
from utils.helpers import format_currency

class BatchEditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Batch Edit Parts")
        self.setMinimumWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Leave empty to keep unchanged")
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Leave empty to keep unchanged")
        
        layout.addRow("Category:", self.category_input)
        layout.addRow("Location:", self.location_input)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Apply Batch Edit")
        save_btn.setProperty("class", "Primary")
        save_btn.setDefault(True)
        save_btn.setAutoDefault(True)
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addRow(btn_layout)

    def get_data(self):
        return {
            'category': self.category_input.text().strip(),
            'location': self.location_input.text().strip()
        }

class PartDialog(QDialog):
    def __init__(self, parent=None, part_data=None):
        super().__init__(parent)
        self.part_data = part_data
        self.setWindowTitle("Add Part" if not part_data else "Edit Part")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        self.number_input = QLineEdit()
        self.category_input = QLineEdit()
        self.location_input = QLineEdit()
        
        self.min_qty_input = QSpinBox()
        self.min_qty_input.setRange(0, 10000)
        self.min_qty_input.setValue(5)
        self.min_qty_input.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.purchase_price_input = QDoubleSpinBox()
        self.purchase_price_input.setRange(0, 1000000)
        self.purchase_price_input.setDecimals(2)
        self.purchase_price_input.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.selling_price_input = QDoubleSpinBox()
        self.selling_price_input.setRange(0, 1000000)
        self.selling_price_input.setDecimals(2)
        self.selling_price_input.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        if self.part_data:
            self.name_input.setText(self.part_data.get('part_name', ''))
            self.number_input.setText(self.part_data.get('part_number', ''))
            self.category_input.setText(self.part_data.get('category', ''))
            self.location_input.setText(self.part_data.get('location', ''))
            self.min_qty_input.setValue(self.part_data.get('min_quantity', 5))
            self.purchase_price_input.setValue(self.part_data.get('purchase_price', 0))
            self.selling_price_input.setValue(self.part_data.get('selling_price', 0))
            
        layout.addRow("Part Name:", self.name_input)
        layout.addRow("Part Number:", self.number_input)
        layout.addRow("Category:", self.category_input)
        layout.addRow("Location:", self.location_input)
        layout.addRow("Min Quantity:", self.min_qty_input)
        layout.addRow("Purchase Price:", self.purchase_price_input)
        layout.addRow("Selling Price:", self.selling_price_input)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setProperty("class", "Primary")
        save_btn.setDefault(True)
        save_btn.setAutoDefault(True)
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addRow(btn_layout)

    def get_data(self):
        return {
            'part_name': self.name_input.text().strip(),
            'part_number': self.number_input.text().strip(),
            'category': self.category_input.text().strip(),
            'location': self.location_input.text().strip(),
            'min_quantity': self.min_qty_input.value(),
            'purchase_price': self.purchase_price_input.value(),
            'selling_price': self.selling_price_input.value()
        }

class InventoryScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Parts Inventory")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search parts by name or number...")
        self.search_input.textChanged.connect(self.load_data)
        self.search_input.setFixedWidth(300)
        
        add_btn = QPushButton("+ Add Part")
        add_btn.setProperty("class", "Primary")
        add_btn.clicked.connect(self.add_part)
        
        export_btn = QPushButton("Export CSV")
        export_btn.clicked.connect(self.export_csv)
        
        import_btn = QPushButton("Import CSV")
        import_btn.clicked.connect(self.import_csv)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(export_btn)
        header_layout.addWidget(import_btn)
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget(0, 8)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setHorizontalHeaderLabels(["ID", "Part Number", "Part Name", "Category", "Location", "Qty", "Pur. Price", "Sell. Price"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.edit_part)
        
        layout.addWidget(self.table)
        
        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        
        edit_btn = QPushButton("Edit Selected")
        edit_btn.clicked.connect(self.edit_part)
        
        batch_edit_btn = QPushButton("Batch Edit Selected")
        batch_edit_btn.clicked.connect(self.batch_edit_parts)
        
        delete_btn = QPushButton("Delete Selected")
        delete_btn.setStyleSheet("background-color: #EF4444; color: white; border-radius: 8px; border: none;")
        delete_btn.clicked.connect(self.delete_part)
        
        actions_layout.addWidget(batch_edit_btn)
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        layout.addLayout(actions_layout)

    def load_data(self):
        query = self.search_input.text().strip()
        if query:
            parts = search_parts(query)
        else:
            parts = get_all_parts()
            
        self.table.setRowCount(0)
        for row, part in enumerate(parts):
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(part['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(part['part_number']))
            self.table.setItem(row, 2, QTableWidgetItem(part['part_name']))
            self.table.setItem(row, 3, QTableWidgetItem(part['category'] or ""))
            self.table.setItem(row, 4, QTableWidgetItem(part['location'] or ""))
            
            qty_item = QTableWidgetItem(str(part['quantity']))
            if part['quantity'] <= part['min_quantity']:
                qty_item.setBackground(QColor("#450A0A")) # Dark red bg for dark theme
                qty_item.setForeground(QColor("#FCA5A5")) # Light red text
            self.table.setItem(row, 5, qty_item)
            
            self.table.setItem(row, 6, QTableWidgetItem(format_currency(part['purchase_price'])))
            self.table.setItem(row, 7, QTableWidgetItem(format_currency(part['selling_price'])))

    def get_selected_part_id(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        return int(self.table.item(row, 0).text())

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Inventory", "inventory.csv", "CSV Files (*.csv)")
        if not path: return
        try:
            import csv
            parts = get_all_parts()
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Part Number", "Part Name", "Category", "Location", "Quantity", "Min Quantity", "Purchase Price", "Selling Price"])
                for p in parts:
                    writer.writerow([
                        p['part_number'], p['part_name'], p['category'], p['location'],
                        p['quantity'], p['min_quantity'], p['purchase_price'], p['selling_price']
                    ])
            ToastNotification.show_toast(self.window(), "Inventory exported successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not export:\n{str(e)}")

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Inventory", "", "CSV Files (*.csv)")
        if not path: return
        try:
            import csv
            from database.models import execute_query
            with open(path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                imported = 0
                for row in reader:
                    part_num = row.get('Part Number', '').strip()
                    part_name = row.get('Part Name', '').strip()
                    if part_num and part_name:
                        try:
                            qty = int(row.get('Quantity', 0) or 0)
                            execute_query("""
                                INSERT INTO parts (part_number, part_name, category, location, quantity, min_quantity, purchase_price, selling_price)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                part_num, part_name,
                                row.get('Category', '').strip(), row.get('Location', '').strip(),
                                qty, int(row.get('Min Quantity', 5) or 5),
                                float(row.get('Purchase Price', 0) or 0), float(row.get('Selling Price', 0) or 0)
                            ), commit=True)
                            imported += 1
                        except: pass
            self.load_data()
            ToastNotification.show_toast(self.window(), f"Imported {imported} new parts successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not import:\n{str(e)}")

    def add_part(self):
        dialog = PartDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['part_name'] or not data['part_number']:
                QMessageBox.warning(self, "Error", "Part Name and Part Number are required.")
                return
            try:
                add_part(data)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def batch_edit_parts(self):
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select at least one part to edit.")
            return
            
        dialog = BatchEditDialog(self)
        if dialog.exec():
            new_data = dialog.get_data()
            if not new_data['category'] and not new_data['location']:
                return 
                
            from database.models import get_part_by_id, update_part
            for row in selected_rows:
                part_id = int(self.table.item(row, 0).text())
                part = dict(get_part_by_id(part_id))
                if new_data['category']: part['category'] = new_data['category']
                if new_data['location']: part['location'] = new_data['location']
                update_part(part_id, part)
            self.load_data()

    def edit_part(self, item=None):
        part_id = self.get_selected_part_id()
        if not part_id:
            QMessageBox.information(self, "Select Part", "Please select a part to edit.")
            return
            
        # Get part details
        from database.models import get_part_by_id
        part_data = get_part_by_id(part_id)
        
        dialog = PartDialog(self, part_data)
        if dialog.exec():
            data = dialog.get_data()
            if not data['part_name'] or not data['part_number']:
                QMessageBox.warning(self, "Error", "Part Name and Part Number are required.")
                return
            try:
                update_part(part_id, data)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", str(e))

    def delete_part(self):
        part_id = self.get_selected_part_id()
        if not part_id:
            QMessageBox.information(self, "Select Part", "Please select a part to delete.")
            return
            
        reply = QMessageBox.question(self, "Confirm Delete", 
                                     "Are you sure you want to delete this part?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                                     
        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_part(part_id)
                self.load_data()
            except ValueError as e:
                QMessageBox.warning(self, "Cannot Delete", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Database Error", str(e))

# We need to import QColor
from PyQt6.QtGui import QColor
