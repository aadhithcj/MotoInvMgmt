import sqlite3
import os

DB_NAME = "gearfield.db"

def seed():
    if not os.path.exists(DB_NAME):
        print(f"Database {DB_NAME} not found. Launch main.py first to initialize, or we will initialize now.")
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        # 1. Clear existing data to ensure a clean state
        cursor.execute("DELETE FROM supplier_bill_items")
        cursor.execute("DELETE FROM supplier_bills")
        cursor.execute("DELETE FROM customer_bill_items")
        cursor.execute("DELETE FROM customer_bills")
        cursor.execute("DELETE FROM parts")
        cursor.execute("DELETE FROM suppliers")

        # Reset autoincrement sequences
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('parts', 'suppliers', 'supplier_bills', 'customer_bills')")

        # 2. Insert Sample Suppliers
        suppliers = [
            ("Apex Motor Spares Wholesaler", "+91 98765 43210", "12/A, Industrial Area, Phase-2, Bangalore"),
            ("Tornado Parts Ltd.", "+91 87654 32109", "Plot 45, G.I.D.C., Sector 4, Chennai"),
            ("SuperDrive Chain & Gears", "+91 76543 21098", "Warehouse 5, Outer Ring Road, Pune")
        ]
        
        cursor.executemany("""
            INSERT INTO suppliers (name, phone, address) 
            VALUES (?, ?, ?)
        """, suppliers)
        print(f"Inserted {len(suppliers)} suppliers.")

        # Get supplier IDs
        cursor.execute("SELECT id, name FROM suppliers")
        supplier_ids = {row[1]: row[0] for row in cursor.fetchall()}

        # 3. Insert Sample Parts
        # quantity <= min_quantity will trigger low-stock alerts
        parts = [
            # Brakes
            ("Front Brake Pad (Yamaha FZ)", "BP-F890", "Brakes", "Shelf A-1", 15, 5, 450.00, 650.00),
            ("Rear Brake Pad (Yamaha FZ)", "BP-R120", "Brakes", "Shelf A-2", 3, 5, 400.00, 580.00), # Low Stock
            ("Brake Caliper Assembly", "BC-Y150", "Brakes", "Rack E-2", 2, 2, 1800.00, 2400.00),
            
            # Lubricants & Filters
            ("Engine Oil 1L (10W40 Synthetic)", "OIL-10W40", "Lubricants", "Shelf B-5", 25, 10, 250.00, 380.00),
            ("Air Filter (Honda Activa)", "FLT-ACT5G", "Filters", "Shelf B-2", 4, 10, 120.00, 200.00), # Low Stock
            ("Oil Filter (KTM Duke)", "FLT-KTM390", "Filters", "Shelf B-3", 12, 5, 180.00, 280.00),

            # Electrical
            ("NGK Spark Plug (Iridium)", "SP-NGK9", "Electrical", "Drawer C-3", 8, 15, 90.00, 160.00), # Low Stock
            ("Halogen Headlight Bulb 12V", "BLB-H4-12V", "Electrical", "Drawer C-1", 20, 8, 110.00, 180.00),
            ("Exide Maintenance Free Battery", "BAT-EX12V", "Electrical", "Floor Area 1", 5, 3, 1450.00, 1900.00),

            # Drivetrain
            ("DID Drive Chain 120L (520 size)", "CHN-DID520", "Drivetrain", "Rack D-1", 12, 3, 1200.00, 1800.00),
            ("Rear Sprocket 42T (Yamaha)", "SPK-R42T", "Drivetrain", "Rack D-3", 1, 3, 650.00, 950.00), # Low Stock
            ("Front Sprocket 14T (Yamaha)", "SPK-F14T", "Drivetrain", "Rack D-4", 6, 3, 220.00, 350.00)
        ]

        cursor.executemany("""
            INSERT INTO parts (part_name, part_number, category, location, quantity, min_quantity, purchase_price, selling_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, parts)
        print(f"Inserted {len(parts)} parts.")

        # 4. Save Shop details
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('shop_name', 'Royal Motorbike Spares')")
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('shop_phone', '+91 90000 12345')")
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('shop_address', '100 Feet Ring Road, JP Nagar, 2nd Phase, Bangalore - 560078')")

        conn.commit()
        print("Database seeded successfully with sample test data!")
    except sqlite3.Error as e:
        print(f"Seeding error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    seed()
