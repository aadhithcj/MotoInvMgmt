from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMessageBox, QFileDialog, QDialog, QFormLayout, QLineEdit, 
                             QDateEdit, QComboBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor

from database.models import (get_all_customer_bills, get_all_parts, save_customer_bill)
from utils.pdf_extractor_customer import extract_customer_bill
from utils.helpers import format_currency

class CustomerReviewDialog(QDialog):
    def __init__(self, parent, extracted_data):
        super().__init__(parent)
        self.setWindowTitle("Review Customer Bill")
        self.setMinimumSize(1000, 600)
        self.extracted_data = extracted_data
        self.all_parts = get_all_parts()
        
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
        
        self.cust_name_input = QLineEdit()
        self.cust_phone_input = QLineEdit()
        
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0, 1000000)
        self.discount_input.setDecimals(2)
        
        self.total_input = QDoubleSpinBox()
        self.total_input.setRange(0, 10000000)
        self.total_input.setDecimals(2)
        
        header_group.addRow("Bill Number:", self.bill_no_input)
        header_group.addRow("Date:", self.date_input)
        header_group.addRow("Customer Name:", self.cust_name_input)
        header_group.addRow("Customer Phone:", self.cust_phone_input)
        header_group.addRow("Discount:", self.discount_input)
        header_group.addRow("Total Amount:", self.total_input)
        
        layout.addLayout(header_group)
        
        # --- Items Table ---
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Part Number", "Part Name", "Matched Part", "Action", "Quantity", "Unit Price"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
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
            
        self.cust_name_input.setText(h_data.get('customer_name', ''))
        self.cust_phone_input.setText(h_data.get('customer_phone', ''))
        self.discount_input.setValue(h_data.get('discount', 0.0))
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
        match_type = "RED" # RED, YELLOW, GREEN
        
        for i, p in enumerate(self.all_parts):
            display_text = f"[{p['part_number']}] {p['part_name']} (Stock: {p['quantity']})"
            combo.addItem(display_text, p['id'])
            
            # Exact match by part number
            if p['part_number'] == part_no and part_no != "":
                best_match_idx = i + 1
                match_type = "GREEN"
            # Case insensitive match by name (only if no exact part number match yet)
            elif p['part_name'].lower() == part_name.lower() and match_type != "GREEN" and part_name != "":
                best_match_idx = i + 1
                match_type = "YELLOW"
                
        combo.setCurrentIndex(best_match_idx)
        combo.currentIndexChanged.connect(self.validate_rows)
        self.table.setCellWidget(row, 2, combo)
        
        # Store match type metadata on item
        p_no_item.setData(Qt.ItemDataRole.UserRole, match_type)
        
        # Action button (Remove Row or Match)
        action_btn = QPushButton("Remove")
        action_btn.clicked.connect(lambda _, r=row: self.remove_row(r))
        self.table.setCellWidget(row, 3, action_btn)

    def add_empty_row(self):
        self.add_row("", "", 1, 0.0)
        self.validate_rows()

    def remove_row(self, row):
        reply = QMessageBox.question(self, "Remove Row", "Are you sure you want to remove this row?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.table.removeRow(row)
            self.validate_rows()

    def validate_rows(self):
        unmatched_count = 0
        insufficient_stock_count = 0
        
        # Map of part_id -> total requested quantity in this bill
        # to ensure the combined quantities don't exceed stock
        part_totals = {}
        
        for row in range(self.table.rowCount()):
            combo = self.table.cellWidget(row, 2)
            if not combo: continue
            
            part_id = combo.currentData()
            
            # Validate numeric inputs
            qty_text = self.table.item(row, 4).text()
            try:
                qty = int(qty_text)
            except ValueError:
                qty = 0
                
            if part_id is None:
                # RED
                self.set_row_color(row, "#450A0A") # Red bg
                unmatched_count += 1
            else:
                # Determine color based on initial match type or just green if manually linked
                # Let's check matching type:
                # We can also check if quantity > stock
                part_info = next((p for p in self.all_parts if p['id'] == part_id), None)
                if part_info:
                    part_totals[part_id] = part_totals.get(part_id, 0) + qty
                    
                    # Row color rules
                    # Initial match type metadata
                    p_no_item = self.table.item(row, 0)
                    initial_match_type = p_no_item.data(Qt.ItemDataRole.UserRole) if p_no_item else None
                    
                    if part_totals[part_id] > part_info['quantity']:
                        self.set_row_color(row, "#7F1D1D") # Dark Red for out of stock
                        insufficient_stock_count += 1
                    elif initial_match_type == "YELLOW" and combo.currentIndex() == (self.all_parts.index(part_info) + 1):
                        self.set_row_color(row, "#713F12") # Dark Yellow for name-only match
                    else:
                        self.set_row_color(row, "#064E3B") # Green for normal matched
                else:
                    self.set_row_color(row, "#450A0A")
                    unmatched_count += 1
                    
        status_msg = f"{unmatched_count} unmatched rows."
        if insufficient_stock_count > 0:
            status_msg += f" {insufficient_stock_count} rows have insufficient stock."
            
        self.status_lbl.setText(status_msg)
        self.confirm_btn.setEnabled(unmatched_count == 0 and insufficient_stock_count == 0 and self.table.rowCount() > 0)

    def set_row_color(self, row, hex_color):
        color = QColor(hex_color)
        for col in [0, 1, 4, 5]:
            item = self.table.item(row, col)
            if item:
                item.setBackground(color)

    def confirm(self):
        items_data = []
        for row in range(self.table.rowCount()):
            combo = self.table.cellWidget(row, 2)
            part_id = combo.currentData()
            qty = int(self.table.item(row, 4).text())
            price = float(self.table.item(row, 5).text())
            
            items_data.append({
                'part_id': part_id,
                'quantity': qty,
                'unit_price': price
            })
            
        bill_data = {
            'bill_number': self.bill_no_input.text().strip(),
            'customer_name': self.cust_name_input.text().strip(),
            'customer_phone': self.cust_phone_input.text().strip(),
            'discount': self.discount_input.value(),
            'total_amount': self.total_input.value(),
            'bill_date': self.date_input.date().toString("yyyy-MM-dd")
        }
        
        try:
            save_customer_bill(bill_data, items_data)
            
            # Check for low stock warnings after successful transaction
            low_stock_warnings = []
            # Fetch updated parts
            updated_parts = get_all_parts()
            for item in items_data:
                part = next((p for p in updated_parts if p['id'] == item['part_id']), None)
                if part and part['quantity'] <= part['min_quantity']:
                    low_stock_warnings.append(f"- {part['part_name']} (Qty: {part['quantity']}, Min: {part['min_quantity']})")
            
            msg = "Bill saved and stock updated successfully."
            if low_stock_warnings:
                msg += "\n\n⚠️ LOW STOCK WARNING:\n" + "\n".join(low_stock_warnings)
                
            QMessageBox.information(self, "Success", msg)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

class CustomerBillsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Customer Bills")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        upload_btn = QPushButton("Upload Bill PDF")
        upload_btn.setProperty("class", "Primary")
        upload_btn.clicked.connect(self.upload_pdf)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(upload_btn)
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Date", "Bill No.", "Customer", "Phone", "Amount", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)

    def load_data(self):
        bills = get_all_customer_bills()
        self.table.setRowCount(0)
        for row, bill in enumerate(bills):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(bill['bill_date'].split(' ')[0]))
            self.table.setItem(row, 1, QTableWidgetItem(bill['bill_number']))
            self.table.setItem(row, 2, QTableWidgetItem(bill['customer_name'] or "Unknown"))
            self.table.setItem(row, 3, QTableWidgetItem(bill['customer_phone'] or ""))
            self.table.setItem(row, 4, QTableWidgetItem(format_currency(bill['total_amount'])))
            
            status_item = QTableWidgetItem("Confirmed")
            status_item.setForeground(QColor("#4ADE80"))
            self.table.setItem(row, 5, status_item)

    def upload_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Customer Bill PDF", "", "PDF Files (*.pdf)")
        if not path:
            return
            
        try:
            extracted = extract_customer_bill(path)
            dialog = CustomerReviewDialog(self, extracted)
            if dialog.exec():
                self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Extraction Error", f"Failed to process PDF:\n{str(e)}")
