from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QFrame, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from database.models import get_setting, set_setting

# Import Screens
from .dashboard import DashboardScreen
from .inventory import InventoryScreen
from .supplier_bills import SupplierBillsScreen
from .customer_bills import CustomerBillsScreen
from .suppliers import SuppliersScreen
from .customers import CustomersScreen
from .reports import ReportsScreen
from .settings import SettingsScreen

class MainWindow(QMainWindow):
    def __init__(self, app_ref, dark_style, light_style):
        super().__init__()
        self.app_ref = app_ref
        self.dark_style = dark_style
        self.light_style = light_style
        
        self.setWindowTitle("Gearfield Inventory Management")
        self.resize(1200, 800)
        
        self.current_theme = get_setting('theme', 'dark')

        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 20)
        sidebar_layout.setSpacing(5)

        # Brand Label
        brand_label = QLabel("GEARFIELD")
        brand_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #F97316; padding-top: 20px; padding-left: 20px; padding-bottom: 20px;")
        sidebar_layout.addWidget(brand_label)

        # Navigation Buttons
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", DashboardScreen),
            ("Inventory", InventoryScreen),
            ("Supplier Bills", SupplierBillsScreen),
            ("Customer Bills", CustomerBillsScreen),
            ("Suppliers", SuppliersScreen),
            ("Customers", CustomersScreen),
            ("Reports", ReportsScreen),
            ("Settings", SettingsScreen),
        ]

        self.stacked_widget = QStackedWidget()
        
        for idx, (name, WidgetClass) in enumerate(nav_items):
            btn = QPushButton(name)
            btn.setObjectName(f"Nav_{name}")
            btn.setProperty("class", "NavButton")
            btn.setCheckable(True)
            if idx == 0:
                btn.setChecked(True)
                
            # Create instance
            screen_instance = WidgetClass()
            self.stacked_widget.addWidget(screen_instance)
            
            btn.clicked.connect(lambda checked, index=idx, b=btn: self.switch_screen(index, b))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[name] = btn

        sidebar_layout.addStretch()

        # Theme Toggle Button
        self.theme_btn = QPushButton("Toggle Theme")
        self.theme_btn.setProperty("class", "NavButton")
        self.theme_btn.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.theme_btn)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_widget)
        
        # Initial Screen Load
        self.switch_screen(0, self.nav_buttons["Dashboard"])

    def setup_shortcuts(self):
        # New Bill (Ctrl+N)
        shortcut_new = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut_new.activated.connect(self.action_new_bill)
        
        # Focus Search (Ctrl+F)
        shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_search.activated.connect(self.action_focus_search)
        
        # Reload (F5)
        shortcut_reload = QShortcut(QKeySequence("F5"), self)
        shortcut_reload.activated.connect(self.action_reload)

    def action_new_bill(self):
        # Switch to Customer Bills tab (index 3)
        self.switch_screen(3, self.nav_buttons["Customer Bills"])
        widget = self.stacked_widget.currentWidget()
        if hasattr(widget, 'create_bill'):
            widget.create_bill()

    def action_focus_search(self):
        widget = self.stacked_widget.currentWidget()
        if hasattr(widget, 'search_input'):
            widget.search_input.setFocus()

    def action_reload(self):
        widget = self.stacked_widget.currentWidget()
        if hasattr(widget, 'load_data'):
            widget.load_data()

    def switch_screen(self, index, button):
        # Uncheck all others
        for btn in self.nav_buttons.values():
            if btn != button:
                btn.setChecked(False)
        button.setChecked(True)
        self.stacked_widget.setCurrentIndex(index)
        
        # Refresh screen data if method exists
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'load_data'):
            current_widget.load_data()

    def toggle_theme(self):
        if self.current_theme == 'dark':
            self.current_theme = 'light'
            self.app_ref.setStyleSheet(self.light_style)
        else:
            self.current_theme = 'dark'
            self.app_ref.setStyleSheet(self.dark_style)
        
        set_setting('theme', self.current_theme)
