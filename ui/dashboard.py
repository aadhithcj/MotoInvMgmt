from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
from PyQt6.QtCore import Qt
from database.models import get_dashboard_stats, get_low_stock_parts, get_recent_bills, get_sales_over_time
from utils.helpers import format_currency
import pyqtgraph as pg

class StatCard(QFrame):
    def __init__(self, title, value, color="#F97316"):
        super().__init__()
        self.setObjectName("StatCard")
        layout = QVBoxLayout(self)
        
        title_lbl = QLabel(title)
        title_lbl.setObjectName("StatCardTitle")
        
        self.val_lbl = QLabel(str(value))
        self.val_lbl.setObjectName("StatCardValue")
        self.val_lbl.setStyleSheet(f"color: {color};")
        
        layout.addWidget(title_lbl)
        layout.addWidget(self.val_lbl)
        
    def update_value(self, value):
        self.val_lbl.setText(str(value))

class DashboardScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Stats Row
        stats_layout = QHBoxLayout()
        self.card_parts = StatCard("Total Parts", "0")
        self.card_value = StatCard("Inventory Value", "0")
        self.card_low = StatCard("Low Stock", "0", color="#EF4444")
        self.card_bills = StatCard("Bills Today", "0")
        
        stats_layout.addWidget(self.card_parts)
        stats_layout.addWidget(self.card_value)
        stats_layout.addWidget(self.card_low)
        stats_layout.addWidget(self.card_bills)
        layout.addLayout(stats_layout)
        
        # Chart Layout
        self.chart_frame = QFrame()
        self.chart_frame.setObjectName("StatCard") # Reuse styling
        chart_layout = QVBoxLayout(self.chart_frame)
        
        pg.setConfigOptions(antialias=True)
        self.plot_widget = pg.PlotWidget()
        chart_layout.addWidget(self.plot_widget)
        layout.addWidget(self.chart_frame)
        
        # Tables Layout
        tables_layout = QHBoxLayout()
        
        # Low Stock Table
        low_stock_group = QVBoxLayout()
        ls_title = QLabel("Low Stock Alert")
        ls_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.low_stock_table = QTableWidget(0, 4)
        self.low_stock_table.verticalHeader().setDefaultSectionSize(40)
        self.low_stock_table.setHorizontalHeaderLabels(["Part #", "Name", "Qty", "Min Qty"])
        self.low_stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.low_stock_table.setStyleSheet("QTableWidget { border: 1px solid rgba(239, 68, 68, 0.5); border-radius: 12px; }")
        
        low_stock_group.addWidget(ls_title)
        low_stock_group.addWidget(self.low_stock_table)
        tables_layout.addLayout(low_stock_group)
        
        # Recent Bills Table
        recent_group = QVBoxLayout()
        rb_title = QLabel("Recent Bills")
        rb_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.recent_bills_table = QTableWidget(0, 4)
        self.recent_bills_table.verticalHeader().setDefaultSectionSize(40)
        self.recent_bills_table.setHorizontalHeaderLabels(["Date", "Type", "Bill #", "Amount"])
        self.recent_bills_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        recent_group.addWidget(rb_title)
        recent_group.addWidget(self.recent_bills_table)
        tables_layout.addLayout(recent_group)
        
        layout.addLayout(tables_layout)

    def load_data(self):
        # Stats
        stats = get_dashboard_stats()
        self.card_parts.update_value(stats.get('total_parts', 0))
        self.card_value.update_value(format_currency(stats.get('total_value', 0)))
        self.card_low.update_value(stats.get('low_stock', 0))
        self.card_bills.update_value(stats.get('bills_today', 0))
        
        # Update Chart
        sales_data = get_sales_over_time(30)
        self.plot_widget.clear()
        
        is_dark = self.palette().window().color().lightness() < 128
        bg_color = (23, 32, 51) if is_dark else (255, 255, 255)
        text_color = (148, 163, 184) if is_dark else (100, 116, 139)
        line_color = (249, 115, 22)
        grid_color = (255, 255, 255, 25) if is_dark else (0, 0, 0, 25)
        fill_color = (249, 115, 22, 40)
        
        self.plot_widget.setBackground(bg_color)
        self.plot_widget.setTitle("Sales Over Last 30 Days", color=text_color, size="12pt")
        self.plot_widget.getAxis("left").setPen(text_color)
        self.plot_widget.getAxis("left").setTextPen(text_color)
        self.plot_widget.getAxis("bottom").setPen(text_color)
        self.plot_widget.getAxis("bottom").setTextPen(text_color)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        if sales_data:
            dates = [row['bdate'][-5:] for row in sales_data]
            x_dict = dict(enumerate(dates))
            x_axis = self.plot_widget.getAxis('bottom')
            x_axis.setTicks([list(x_dict.items())])
            
            x = list(range(len(dates)))
            y = [row['total'] for row in sales_data]
            
            pen = pg.mkPen(color=line_color, width=3)
            curve = self.plot_widget.plot(x, y, pen=pen, symbol='o', symbolSize=8, symbolBrush=line_color)
            
            fill = pg.FillBetweenItem(curve1=curve, brush=pg.mkBrush(color=fill_color), curve2=pg.PlotCurveItem(x, [0]*len(x)))
            self.plot_widget.addItem(fill)
        
        # Low Stock
        low_stock = get_low_stock_parts()
        self.low_stock_table.setRowCount(0)
        for row, part in enumerate(low_stock):
            self.low_stock_table.insertRow(row)
            self.low_stock_table.setItem(row, 0, QTableWidgetItem(part['part_name']))
            self.low_stock_table.setItem(row, 1, QTableWidgetItem(part['part_number']))
            
            qty_item = QTableWidgetItem(str(part['quantity']))
            qty_item.setForeground(Qt.GlobalColor.red)
            self.low_stock_table.setItem(row, 2, qty_item)
            
            self.low_stock_table.setItem(row, 3, QTableWidgetItem(str(part['min_quantity'])))
            
        # Recent Bills
        recent_bills = get_recent_bills(limit=10)
        self.recent_bills_table.setRowCount(0)
        for row, bill in enumerate(recent_bills):
            self.recent_bills_table.insertRow(row)
            self.recent_bills_table.setItem(row, 0, QTableWidgetItem(bill['bill_date'].split(' ')[0]))
            
            type_item = QTableWidgetItem(bill['type'])
            if bill['type'] == 'Supplier':
                type_item.setForeground(Qt.GlobalColor.green)
            else:
                type_item.setForeground(Qt.GlobalColor.yellow)
            self.recent_bills_table.setItem(row, 1, type_item)
            
            self.recent_bills_table.setItem(row, 2, QTableWidgetItem(bill['bill_number']))
            self.recent_bills_table.setItem(row, 3, QTableWidgetItem(format_currency(bill['total_amount'])))
