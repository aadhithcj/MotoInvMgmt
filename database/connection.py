import sqlite3
import os
import sys
import shutil

DB_NAME = "gearfield.db"

# Migrate old database name if it exists and new one does not
if not os.path.exists(DB_NAME) and os.path.exists("motoshop.db"):
    try:
        os.rename("motoshop.db", DB_NAME)
        print("Migrated database file from motoshop.db to gearfield.db")
    except Exception as e:
        print(f"Database migration failed: {e}")

# If database doesn't exist locally, check if a pre-populated database is bundled inside the executable
if not os.path.exists(DB_NAME):
    meipass = getattr(sys, '_MEIPASS', None)
    if meipass:
        bundled_db = os.path.join(meipass, DB_NAME)
        if os.path.exists(bundled_db):
            try:
                shutil.copy(bundled_db, DB_NAME)
                print("Extracted bundled test database to local directory")
            except Exception as e:
                print(f"Failed to extract bundled database: {e}")

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name
    # Enforce foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Creates the database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Table: parts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_name TEXT NOT NULL,
                part_number TEXT UNIQUE NOT NULL,
                category TEXT,
                location TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                min_quantity INTEGER DEFAULT 5,
                purchase_price REAL DEFAULT 0,
                selling_price REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table: suppliers
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT
            )
        ''')

        # Table: supplier_bills
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplier_bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_number TEXT NOT NULL,
                supplier_id INTEGER REFERENCES suppliers(id),
                pdf_filename TEXT,
                total_amount REAL,
                bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                status TEXT DEFAULT 'Paid'
            )
        ''')

        # Migration: Add status column to customer_bills if it doesn't exist
        try:
            cursor.execute("ALTER TABLE customer_bills ADD COLUMN status TEXT DEFAULT 'Paid'")
        except sqlite3.OperationalError:
            pass

        # Table: supplier_bill_items
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplier_bill_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id INTEGER REFERENCES supplier_bills(id),
                part_id INTEGER REFERENCES parts(id),
                quantity INTEGER NOT NULL,
                unit_price REAL DEFAULT 0
            )
        ''')

        # Table: customer_bills
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_number TEXT NOT NULL,
                customer_name TEXT,
                customer_phone TEXT,
                pdf_filename TEXT,
                total_amount REAL,
                discount REAL DEFAULT 0,
                bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')

        # Table: customer_bill_items
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_bill_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id INTEGER REFERENCES customer_bills(id),
                part_id INTEGER REFERENCES parts(id),
                quantity INTEGER NOT NULL,
                unit_price REAL DEFAULT 0
            )
        ''')

        # Table: settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        # Initialize default settings if not exists
        cursor.execute("SELECT COUNT(*) FROM settings WHERE key='theme'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO settings (key, value) VALUES ('theme', 'dark')")
            
        cursor.execute("SELECT COUNT(*) FROM settings WHERE key='customer_bill_mapping'")
        if cursor.fetchone()[0] == 0:
            # Default JSON mapping
            default_mapping = '{"part_number": ["part no", "part number", "code", "item code"], "part_name": ["description", "item", "name", "part name"], "quantity": ["qty", "quantity", "units"], "unit_price": ["price", "unit price", "rate"], "total": ["total", "amount", "line total"]}'
            cursor.execute("INSERT INTO settings (key, value) VALUES ('customer_bill_mapping', ?)", (default_mapping,))

        # Initialize shop and bank defaults
        defaults = {
            'shop_name': 'Gearfield',
            'shop_phone': '99463 53623',
            'shop_email': 'contact@gearfield.in',
            'shop_address': 'Pallipadan Building, Karukutty P O\nKarayamparambu, Angamaly',
            'shop_gstin': '32AAFFL4488E1ZD',
            'shop_state': 'Kerala, Code: 32',
            'bank_name': 'State Bank of India',
            'bank_ac_no': '12345678901',
            'bank_branch': 'Angamaly',
            'bank_ifsc': 'SBIN0000000'
        }
        for key, val in defaults.items():
            cursor.execute("SELECT COUNT(*) FROM settings WHERE key=?", (key,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, val))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
