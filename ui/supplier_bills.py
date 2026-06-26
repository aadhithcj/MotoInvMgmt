from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMessageBox, QFileDialog, QDialog, QFormLayout, QLineEdit, 
                             QDateEdit, QComboBox, QDoubleSpinBox, QAbstractItemView, QMenu)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor

from .toast import ToastNotification
from database.models import (get_all_supplier_bills, get_all_parts, get_supplier_by_name, 
                             add_supplier, save_supplier_bill, get_all_suppliers)
from utils.pdf_extractor_supplier import extract_supplier_bill
from utils.helpers import format_currency
from .inventory import PartDialog

class SupplierReviewDialog(QDialog):
    def __init__(self, parent, extracted_data):
        super().__init__(parent)
        self.setWindowTitle("Review Supplier Bill")
        self.setMinimumSize(1000, 600)
        self.extracted_data = extracted_data
        self.all_parts = get_all_parts()
        self.all_suppliers = get_all_suppliers()
        
        self.setup_ui()
        self.populate_data()
        self.validate_rows()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # --- Header Section ---
        header_group = QFormLayout()
        
        self.bill_no_input = QLineEdit()
        
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        
        self.supplier_combo = QComboBox()
        self.supplier_combo.setEditable(True)
        for sup in self.all_suppliers:
            self.supplier_combo.addItem(sup['name'], sup['id'])
            
        self.total_input = QDoubleSpinBox()
        self.total_input.setRange(0, 10000000)
        self.total_input.setDecimals(2)
        
        header_group.addRow("Bill Number:", self.bill_no_input)
        header_group.addRow("Date:", self.date_input)
        header_group.addRow("Supplier:", self.supplier_combo)
        header_group.addRow("Total Amount:", self.total_input)
        
        layout.addLayout(header_group)
        
        # --- Items Table ---
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Part Number", "Part Name", "Matched Part", "Action", "Quantity", "Unit Price", "New Part Data"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnHidden(6, True) # Hidden column to store pending new part data
        layout.addWidget(self.table)
        
        # --- Actions ---
        btn_layout = QHBoxLayout()
        
        add_row_btn = QPushButton("+ Add Row")
        add_row_btn.clicked.connect(self.add_empty_row)
        
        self.status_lbl = QLabel("Ready")
        
        self.confirm_btn = QPushButton("Confirm & Update Stock")
        self.confirm_btn.setProperty("class", "Primary")
        self.confirm_btn.clicked.connect(self.confirm)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(add_row_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.status_lbl)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.confirm_btn)
        
        layout.addLayout(btn_layout)

    def populate_data(self):
        # Header
        h_data = self.extracted_data.get('header', {})
        self.bill_no_input.setText(h_data.get('bill_number', ''))
        
        if h_data.get('date'):
            try:
                date_parts = h_data['date'].split('-')
                qdate = QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                self.date_input.setDate(qdate)
            except:
                self.date_input.setDate(QDate.currentDate())
        else:
            self.date_input.setDate(QDate.currentDate())
            
        sup_name = h_data.get('supplier_name', '')
        if sup_name:
            idx = self.supplier_combo.findText(sup_name, Qt.MatchFlag.MatchContains)
            if idx >= 0:
                self.supplier_combo.setCurrentIndex(idx)
            else:
                self.supplier_combo.setCurrentText(sup_name)
                
        self.total_input.setValue(h_data.get('total_amount', 0.0))
        
        # Items
        items = self.extracted_data.get('items', [])
        for item in items:
            self.add_row(item['part_number'], item['part_name'], item['quantity'], item['unit_price'])

    def add_row(self, part_no, part_name, qty, price):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        p_no_item = QTableWidgetItem(part_no)
        p_name_item = QTableWidgetItem(part_name)
        qty_item = QTableWidgetItem(str(qty))
        price_item = QTableWidgetItem(str(price))
        
        self.table.setItem(row, 0, p_no_item)
        self.table.setItem(row, 1, p_name_item)
        self.table.setItem(row, 4, qty_item)
        self.table.setItem(row, 5, price_item)
        
        # Combo for matched part
        combo = QComboBox()
        combo.addItem("--- Unmatched ---", None)
        
        best_match_idx = 0
        for i, p in enumerate(self.all_parts):
            display_text = f"[{p['part_number']}] {p['part_name']}"
            combo.addItem(display_text, p['id'])
            
            # Auto-match logic
            if p['part_number'] == part_no and part_no != "":
                best_match_idx = i + 1 # +1 because of "Unmatched"
            elif p['part_name'].lower() == part_name.lower() and best_match_idx == 0 and part_name != "":
                best_match_idx = i + 1
                
        combo.setCurrentIndex(best_match_idx)
        combo.currentIndexChanged.connect(self.validate_rows)
        self.table.setCellWidget(row, 2, combo)
        
        # Action button (Create New or Remove)
        action_btn = QPushButton("Options")
        action_btn.clicked.connect(lambda _, r=row: self.handle_row_action(r))
        self.table.setCellWidget(row, 3, action_btn)
        
        self.table.setItem(row, 6, QTableWidgetItem("")) # New part data json

    def add_empty_row(self):
        self.add_row("", "", 1, 0.0)
        self.validate_rows()

    def handle_row_action(self, row):
        combo = self.table.cellWidget(row, 2)
        btn = self.table.cellWidget(row, 3)
        menu = QMenu(self)
        
        if combo.currentData() is None:
            create_action = menu.addAction("✨ Create New Part")
            menu.addSeparator()
            remove_action = menu.addAction("🗑️ Remove Row")
            
            action = menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))
            if action == create_action:
                self.create_new_part_for_row(row)
            elif action == remove_action:
                self.table.removeRow(row)
                self.validate_rows()
        else:
            remove_action = menu.addAction("🗑️ Remove Row")
            action = menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))
            if action == remove_action:
                self.table.removeRow(row)
                self.validate_rows()

    def create_new_part_for_row(self, row):
        part_no = self.table.item(row, 0).text().strip()
        part_name = self.table.item(row, 1).text().strip()
        price = float(self.table.item(row, 5).text())
        
        if not part_no and part_name:
            import random
            prefix = "".join([c for c in part_name if c.isalnum()])[:4].upper()
            if not prefix:
                prefix = "PRT"
            part_no = f"{prefix}-{random.randint(1000, 9999)}"
            self.table.item(row, 0).setText(part_no)
            
        initial_data = {
            'part_number': part_no,
            'part_name': part_name,
            'purchase_price': price,
            'selling_price': price * 1.2 # Default 20% markup suggestion
        }
        
        dialog = PartDialog(self, initial_data)
        if dialog.exec():
            new_data = dialog.get_data()
            if not new_data['part_name'] or not new_data['part_number']:
                QMessageBox.warning(self, "Error", "Part Name and Number required.")
                return
                
            import json
            # Store data in hidden column
            self.table.item(row, 6).setText(json.dumps(new_data))
            
            # Update combo visually to show it's pending creation
            combo = self.table.cellWidget(row, 2)
            combo.setItemText(0, f"(NEW) {new_data['part_number']} - {new_data['part_name']}")
            combo.setCurrentIndex(0)
            
            self.validate_rows()

    def validate_rows(self):
        unmatched_count = 0
        for row in range(self.table.rowCount()):
            combo = self.table.cellWidget(row, 2)
            if not combo: continue
            
            is_new = self.table.item(row, 6) and self.table.item(row, 6).text() != ""
            
            if combo.currentData() is None and not is_new:
                # Unmatched and not marked for creation
                self.set_row_color(row, "#450A0A") # Red
                unmatched_count += 1
            elif is_new:
                self.set_row_color(row, "#064E3B") # Green for new pending
            else:
                # Matched
                self.set_row_color(row, "#064E3B") # Green
                
        self.status_lbl.setText(f"{unmatched_count} rows need review.")
        self.confirm_btn.setEnabled(unmatched_count == 0 and self.table.rowCount() > 0)

    def set_row_color(self, row, hex_color):
        color = QColor(hex_color)
        for col in [0, 1, 4, 5]:
            item = self.table.item(row, col)
            if item:
                item.setBackground(color)

    def confirm(self):
        # 1. Ensure supplier exists
        sup_text = self.supplier_combo.currentText().strip()
        
        idx = self.supplier_combo.findText(sup_text, Qt.MatchFlag.MatchExactly)
        if idx >= 0:
            sup_id = self.supplier_combo.itemData(idx)
        else:
            sup_id = None
        
        
        if not sup_id:
            # Need to create supplier
            if not sup_text:
                QMessageBox.warning(self, "Error", "Supplier name is required.")
                return
            try:
                sup_id = add_supplier({'name': sup_text})
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create supplier: {str(e)}")
                return
                
        # 2. Gather Items and New Parts
        items_data = []
        new_parts_data = []
        
        import json
        
        # Using a temporary negative ID for new parts to link them in memory
        temp_id_counter = -1 
        
        for row in range(self.table.rowCount()):
            qty = int(self.table.item(row, 4).text())
            price = float(self.table.item(row, 5).text())
            
            combo = self.table.cellWidget(row, 2)
            part_id = combo.currentData()
            
            new_part_json = self.table.item(row, 6).text()
            
            if not part_id and new_part_json:
                # It's a new part
                p_data = json.loads(new_part_json)
                p_data['_temp_id'] = temp_id_counter
                new_parts_data.append(p_data)
                
                items_data.append({
                    'part_id': p_data, # Pass dict ref, connection.py handles it
                    'quantity': qty,
                    'unit_price': price
                })
                temp_id_counter -= 1
            elif part_id:
                items_data.append({
                    'part_id': part_id,
                    'quantity': qty,
                    'unit_price': price
                })

        # Process temp references
        # connection.save_supplier_bill expects items_data to have actual part_ids
        # Wait, my models.save_supplier_bill logic:
        # if item['part_id'] is a dict (new part), it won't work directly because it expects integer.
        # Let's fix models.py save logic to handle this, or handle it here.
        
        # It's better to pass the data and let models.py handle it. I will adjust the payload.
        # In models.save_supplier_bill, I will pass new_parts_data.
        # But I need to link them.
        
        bill_data = {
            'bill_number': self.bill_no_input.text().strip(),
            'supplier_id': sup_id,
            'bill_date': self.date_input.date().toString("yyyy-MM-dd"),
            'total_amount': self.total_input.value()
        }
        
        try:
            # We will patch save_supplier_bill to handle the item['part_id'] being a dict ref
            save_supplier_bill(bill_data, items_data, new_parts_data)
            ToastNotification.show_toast(self.window(), "Bill saved and stock updated successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

class SupplierBillsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Supplier Bills")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        upload_btn = QPushButton("Upload Bill (PDF/Image)")
        upload_btn.setProperty("class", "Primary")
        upload_btn.clicked.connect(self.upload_pdf)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(upload_btn)
        layout.addLayout(header_layout)
        
        # Filter Row
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Supplier Name or Bill No...")
        self.search_input.textChanged.connect(self.filter_bills)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addYears(-1))
        self.start_date.dateChanged.connect(self.filter_bills)
        filter_layout.addWidget(self.start_date)
        
        filter_layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addDays(1))
        self.end_date.dateChanged.connect(self.filter_bills)
        filter_layout.addWidget(self.end_date)
        
        layout.addLayout(filter_layout)
        
        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Date", "Bill No.", "Supplier", "Amount", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)

    def load_data(self):
        self.bills = get_all_supplier_bills()
        self.filter_bills()

    def filter_bills(self):
        search_txt = self.search_input.text().strip().lower()
        start = self.start_date.date()
        end = self.end_date.date()
        
        self.table.setRowCount(0)
        
        for bill in self.bills:
            # Check Date
            try:
                b_date = QDate.fromString(bill['bill_date'].split(' ')[0], "yyyy-MM-dd")
            except:
                b_date = QDate.currentDate()
                
            if b_date < start or b_date > end:
                continue
                
            # Check Search Text
            bill_num = bill['bill_number'].lower()
            sup_name = (bill['supplier_name'] or "").lower()
            
            if search_txt and (search_txt not in bill_num and search_txt not in sup_name):
                continue
                
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(bill['bill_date'].split(' ')[0]))
            self.table.setItem(row, 1, QTableWidgetItem(bill['bill_number']))
            self.table.setItem(row, 2, QTableWidgetItem(bill['supplier_name'] or "Unknown"))
            self.table.setItem(row, 3, QTableWidgetItem(format_currency(bill['total_amount'])))
            
            status_item = QTableWidgetItem("Confirmed")
            status_item.setForeground(QColor("#4ADE80"))
            self.table.setItem(row, 4, status_item)

    def upload_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Supplier Bill", "", "Bills (*.pdf *.png *.jpg *.jpeg)")
        if not path:
            return
            
        try:
            extracted = extract_supplier_bill(path)
            dialog = SupplierReviewDialog(self, extracted)
            if dialog.exec():
                self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Extraction Error", f"Failed to process PDF:\n{str(e)}")
