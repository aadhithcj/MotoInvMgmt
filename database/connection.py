import sqlite3
import os

DB_NAME = "motoshop.db"

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
                notes TEXT
            )
        ''')

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

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
