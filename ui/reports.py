import csv
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMessageBox, QFileDialog, QTabWidget, QDateEdit)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor
from database.models import execute_query
from utils.helpers import format_currency
from .toast import ToastNotification

class ReportsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("Reports")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        self.tabs = QTabWidget()
        
        # Stock Tab
        self.stock_tab = QWidget()
        self.setup_stock_tab()
        self.tabs.addTab(self.stock_tab, "Stock Report")
        
        # Sales Tab
        self.sales_tab = QWidget()
        self.setup_sales_tab()
        self.tabs.addTab(self.sales_tab, "Sales Report")
        
        # Purchase Tab
        self.purchase_tab = QWidget()
        self.setup_purchase_tab()
        self.tabs.addTab(self.purchase_tab, "Purchase Report")
        
        # Low Stock Alerts Tab
        self.low_stock_tab = QWidget()
        self.setup_low_stock_tab()
        self.tabs.addTab(self.low_stock_tab, "Low Stock Alerts")
        
        layout.addWidget(self.tabs)

    def setup_low_stock_tab(self):
        layout = QVBoxLayout(self.low_stock_tab)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        export_btn = QPushButton("Export CSV")
        export_btn.setProperty("class", "Primary")
        export_btn.clicked.connect(self.export_low_stock)
        btn_layout.addWidget(export_btn)
        
        layout.addLayout(btn_layout)
        
        self.low_stock_table = QTableWidget(0, 7)
        self.low_stock_table.verticalHeader().setDefaultSectionSize(40)
        self.low_stock_table.setHorizontalHeaderLabels(["Part Number", "Part Name", "Category", "Location", "Current Qty", "Min Qty", "Pur. Price"])
        self.low_stock_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.low_stock_table)

    def setup_stock_tab(self):
        layout = QVBoxLayout(self.stock_tab)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        export_btn = QPushButton("Export CSV")
        export_btn.setProperty("class", "Primary")
        export_btn.clicked.connect(self.export_stock)
        btn_layout.addWidget(export_btn)
        
        layout.addLayout(btn_layout)
        
        self.stock_table = QTableWidget(0, 7)
        self.stock_table.verticalHeader().setDefaultSectionSize(40)
        self.stock_table.setHorizontalHeaderLabels(["Part Number", "Part Name", "Category", "Location", "Qty", "Pur. Price", "Total Value"])
        self.stock_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.stock_table)

    def setup_sales_tab(self):
        layout = QVBoxLayout(self.sales_tab)
        
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Start Date:"))
        self.sales_start = QDateEdit()
        self.sales_start.setCalendarPopup(True)
        self.sales_start.setDate(QDate.currentDate().addDays(-30))
        filter_layout.addWidget(self.sales_start)
        
        filter_layout.addWidget(QLabel("End Date:"))
        self.sales_end = QDateEdit()
        self.sales_end.setCalendarPopup(True)
        self.sales_end.setDate(QDate.currentDate())
        filter_layout.addWidget(self.sales_end)
        
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_sales_data)
        filter_layout.addWidget(load_btn)
        
        filter_layout.addStretch()
        
        export_btn = QPushButton("Export CSV")
        export_btn.setProperty("class", "Primary")
        export_btn.clicked.connect(self.export_sales)
        filter_layout.addWidget(export_btn)
        
        layout.addLayout(filter_layout)
        
        self.sales_table = QTableWidget(0, 5)
        self.sales_table.verticalHeader().setDefaultSectionSize(40)
        self.sales_table.setHorizontalHeaderLabels(["Date", "Bill No.", "Part Name", "Qty", "Amount"])
        self.sales_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.sales_table)

    def setup_purchase_tab(self):
        layout = QVBoxLayout(self.purchase_tab)
        
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Start Date:"))
        self.pur_start = QDateEdit()
        self.pur_start.setCalendarPopup(True)
        self.pur_start.setDate(QDate.currentDate().addDays(-30))
        filter_layout.addWidget(self.pur_start)
        
        filter_layout.addWidget(QLabel("End Date:"))
        self.pur_end = QDateEdit()
        self.pur_end.setCalendarPopup(True)
        self.pur_end.setDate(QDate.currentDate())
        filter_layout.addWidget(self.pur_end)
        
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_purchase_data)
        filter_layout.addWidget(load_btn)
        
        filter_layout.addStretch()
        
        export_btn = QPushButton("Export CSV")
        export_btn.setProperty("class", "Primary")
        export_btn.clicked.connect(self.export_purchases)
        filter_layout.addWidget(export_btn)
        
        layout.addLayout(filter_layout)
        
        self.pur_table = QTableWidget(0, 6)
        self.pur_table.verticalHeader().setDefaultSectionSize(40)
        self.pur_table.setHorizontalHeaderLabels(["Date", "Bill No.", "Supplier", "Part Name", "Qty", "Amount"])
        self.pur_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.pur_table)

    def load_data(self):
        # Called when screen switches
        self.load_stock_data()
        self.load_sales_data()
        self.load_purchase_data()
        self.load_low_stock_data()

    def load_stock_data(self):
        parts = execute_query("SELECT * FROM parts ORDER BY part_name", fetchall=True)
        self.stock_table.setRowCount(0)
        for row, part in enumerate(parts):
            self.stock_table.insertRow(row)
            self.stock_table.setItem(row, 0, QTableWidgetItem(part['part_number']))
            self.stock_table.setItem(row, 1, QTableWidgetItem(part['part_name']))
            self.stock_table.setItem(row, 2, QTableWidgetItem(part['category'] or ""))
            self.stock_table.setItem(row, 3, QTableWidgetItem(part['location'] or ""))
            self.stock_table.setItem(row, 4, QTableWidgetItem(str(part['quantity'])))
            self.stock_table.setItem(row, 5, QTableWidgetItem(format_currency(part['purchase_price'])))
            
            total_val = part['quantity'] * part['purchase_price']
            self.stock_table.setItem(row, 6, QTableWidgetItem(format_currency(total_val)))

    def load_sales_data(self):
        start = self.sales_start.date().toString("yyyy-MM-dd")
        end = self.sales_end.date().toString("yyyy-MM-dd")
        
        query = """
            SELECT cb.bill_date, cb.bill_number, p.part_name, cbi.quantity, cbi.quantity * cbi.unit_price as amount
            FROM customer_bill_items cbi
            JOIN customer_bills cb ON cbi.bill_id = cb.id
            JOIN parts p ON cbi.part_id = p.id
            WHERE date(cb.bill_date) BETWEEN ? AND ?
            ORDER BY cb.bill_date DESC
        """
        data = execute_query(query, (start, end), fetchall=True)
        self.sales_table.setRowCount(0)
        for row, item in enumerate(data):
            self.sales_table.insertRow(row)
            self.sales_table.setItem(row, 0, QTableWidgetItem(item['bill_date'].split(' ')[0]))
            self.sales_table.setItem(row, 1, QTableWidgetItem(item['bill_number']))
            self.sales_table.setItem(row, 2, QTableWidgetItem(item['part_name']))
            self.sales_table.setItem(row, 3, QTableWidgetItem(str(item['quantity'])))
            self.sales_table.setItem(row, 4, QTableWidgetItem(format_currency(item['amount'])))

    def load_purchase_data(self):
        start = self.pur_start.date().toString("yyyy-MM-dd")
        end = self.pur_end.date().toString("yyyy-MM-dd")
        
        query = """
            SELECT sb.bill_date, sb.bill_number, s.name as supplier_name, p.part_name, sbi.quantity, sbi.quantity * sbi.unit_price as amount
            FROM supplier_bill_items sbi
            JOIN supplier_bills sb ON sbi.bill_id = sb.id
            LEFT JOIN suppliers s ON sb.supplier_id = s.id
            JOIN parts p ON sbi.part_id = p.id
            WHERE date(sb.bill_date) BETWEEN ? AND ?
            ORDER BY sb.bill_date DESC
        """
        data = execute_query(query, (start, end), fetchall=True)
        self.pur_table.setRowCount(0)
        for row, item in enumerate(data):
            self.pur_table.insertRow(row)
            self.pur_table.setItem(row, 0, QTableWidgetItem(item['bill_date'].split(' ')[0]))
            self.pur_table.setItem(row, 1, QTableWidgetItem(item['bill_number']))
            self.pur_table.setItem(row, 2, QTableWidgetItem(item['supplier_name'] or 'Unknown'))
            self.pur_table.setItem(row, 3, QTableWidgetItem(item['part_name']))
            self.pur_table.setItem(row, 4, QTableWidgetItem(str(item['quantity'])))
            self.pur_table.setItem(row, 5, QTableWidgetItem(format_currency(item['amount'])))

    def load_low_stock_data(self):
        parts = execute_query("SELECT * FROM parts WHERE quantity <= min_quantity ORDER BY quantity ASC", fetchall=True)
        self.low_stock_table.setRowCount(0)
        for row, part in enumerate(parts):
            self.low_stock_table.insertRow(row)
            self.low_stock_table.setItem(row, 0, QTableWidgetItem(part['part_number']))
            self.low_stock_table.setItem(row, 1, QTableWidgetItem(part['part_name']))
            self.low_stock_table.setItem(row, 2, QTableWidgetItem(part['category'] or ""))
            self.low_stock_table.setItem(row, 3, QTableWidgetItem(part['location'] or ""))
            
            qty_item = QTableWidgetItem(str(part['quantity']))
            qty_item.setForeground(QColor("#EF4444"))
            self.low_stock_table.setItem(row, 4, qty_item)
            
            self.low_stock_table.setItem(row, 5, QTableWidgetItem(str(part['min_quantity'])))
            self.low_stock_table.setItem(row, 6, QTableWidgetItem(format_currency(part['purchase_price'])))

    def export_csv(self, table, default_name):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", default_name, "CSV Files (*.csv)")
        if not path:
            return
            
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Header
                headers = []
                for c in range(table.columnCount()):
                    headers.append(table.horizontalHeaderItem(c).text())
                writer.writerow(headers)
                
                # Rows
                for r in range(table.rowCount()):
                    row_data = []
                    for c in range(table.columnCount()):
                        item = table.item(r, c)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
                    
            ToastNotification.show_toast(self.window(), "Export completed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file:\n{str(e)}")

    def export_stock(self):
        self.export_csv(self.stock_table, "stock_report.csv")

    def export_sales(self):
        self.export_csv(self.sales_table, "sales_report.csv")

    def export_purchases(self):
        self.export_csv(self.pur_table, "purchase_report.csv")

    def export_low_stock(self):
        self.export_csv(self.low_stock_table, "reorder_sheet.csv")
