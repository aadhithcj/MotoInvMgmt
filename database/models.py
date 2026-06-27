import sqlite3
from .connection import get_connection

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    conn = get_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if commit:
            conn.commit()
            return cursor.lastrowid
        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if commit:
            conn.rollback()
        raise e
    finally:
        conn.close()

# --- Parts ---

def get_all_parts():
    return execute_query("SELECT * FROM parts", fetchall=True)

def get_part_by_id(part_id):
    return execute_query("SELECT * FROM parts WHERE id = ?", (part_id,), fetchone=True)

def get_part_by_number(part_number):
    return execute_query("SELECT * FROM parts WHERE part_number = ?", (part_number,), fetchone=True)

def get_part_by_name(part_name):
    # Case-insensitive match using COLLATE NOCASE
    return execute_query("SELECT * FROM parts WHERE part_name = ? COLLATE NOCASE", (part_name,), fetchone=True)

def search_parts(query):
    like_query = f"%{query}%"
    return execute_query("SELECT * FROM parts WHERE part_name LIKE ? OR part_number LIKE ?", (like_query, like_query), fetchall=True)

def add_part(data):
    query = """
        INSERT INTO parts (part_name, part_number, category, location, min_quantity, purchase_price, selling_price, quantity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        data['part_name'], data['part_number'], data.get('category', ''), 
        data.get('location', ''), data.get('min_quantity', 5), 
        data.get('purchase_price', 0), data.get('selling_price', 0),
        data.get('quantity', 0)
    )
    return execute_query(query, params, commit=True)

def update_part(part_id, data):
    query = """
        UPDATE parts 
        SET part_name=?, part_number=?, category=?, location=?, min_quantity=?, purchase_price=?, selling_price=?, quantity=?
        WHERE id=?
    """
    params = (
        data['part_name'], data['part_number'], data.get('category', ''), 
        data.get('location', ''), data.get('min_quantity', 5), 
        data.get('purchase_price', 0), data.get('selling_price', 0),
        data.get('quantity', 0),
        part_id
    )
    execute_query(query, params, commit=True)

def delete_part(part_id):
    # Check if part exists in bills
    sup_items = execute_query("SELECT count(*) as c FROM supplier_bill_items WHERE part_id=?", (part_id,), fetchone=True)
    cust_items = execute_query("SELECT count(*) as c FROM customer_bill_items WHERE part_id=?", (part_id,), fetchone=True)
    
    if sup_items['c'] > 0 or cust_items['c'] > 0:
        raise ValueError("Cannot delete part: It is referenced in existing bills.")
        
    execute_query("DELETE FROM parts WHERE id=?", (part_id,), commit=True)

# --- Suppliers ---

def get_all_suppliers():
    return execute_query("SELECT * FROM suppliers", fetchall=True)

def get_supplier_by_name(name):
    return execute_query("SELECT * FROM suppliers WHERE name = ? COLLATE NOCASE", (name,), fetchone=True)

def add_supplier(data):
    return execute_query("INSERT INTO suppliers (name, phone, address) VALUES (?, ?, ?)", 
                         (data['name'], data.get('phone', ''), data.get('address', '')), commit=True)

def update_supplier(supplier_id, data):
    execute_query("UPDATE suppliers SET name=?, phone=?, address=? WHERE id=?", 
                  (data['name'], data.get('phone', ''), data.get('address', ''), supplier_id), commit=True)

def delete_supplier(supplier_id):
    bills = execute_query("SELECT count(*) as c FROM supplier_bills WHERE supplier_id=?", (supplier_id,), fetchone=True)
    if bills['c'] > 0:
        raise ValueError("Cannot delete supplier: They have existing bills.")
    execute_query("DELETE FROM suppliers WHERE id=?", (supplier_id,), commit=True)

# --- Customers ---

def get_all_customers():
    return execute_query("SELECT * FROM customers ORDER BY name ASC", fetchall=True)

def get_customer_by_name(name):
    return execute_query("SELECT * FROM customers WHERE name = ? COLLATE NOCASE", (name,), fetchone=True)

def search_customers(query):
    like_query = f"%{query}%"
    return execute_query("SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? ORDER BY name ASC", 
                         (like_query, like_query), fetchall=True)

def add_customer(data):
    return execute_query("INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)", 
                         (data['name'], data.get('phone', ''), data.get('email', ''), data.get('address', '')), commit=True)

def update_customer(customer_id, data):
    execute_query("UPDATE customers SET name=?, phone=?, email=?, address=? WHERE id=?", 
                  (data['name'], data.get('phone', ''), data.get('email', ''), data.get('address', ''), customer_id), commit=True)

def delete_customer(customer_id):
    bills = execute_query("SELECT count(*) as c FROM customer_bills WHERE customer_id=?", (customer_id,), fetchone=True)
    if bills['c'] > 0:
        raise ValueError("Cannot delete customer: They have existing bills.")
    execute_query("DELETE FROM customers WHERE id=?", (customer_id,), commit=True)

# --- Settings ---

def get_setting(key, default=None):
    res = execute_query("SELECT value FROM settings WHERE key=?", (key,), fetchone=True)
    return res['value'] if res else default

def set_setting(key, value):
    execute_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)), commit=True)

# --- Bills and Transactions ---

def save_supplier_bill(bill_data, items_data, new_parts_data=None):
    """
    Saves a supplier bill, creates new parts if needed, and INCREASES stock.
    Executes within a single transaction.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. Create new parts if any
        if new_parts_data:
            created_parts = {}
            for part in new_parts_data:
                p_num = part.get('part_number')
                
                if p_num and p_num in created_parts:
                    part['id'] = created_parts[p_num]
                    continue
                    
                if p_num:
                    cursor.execute("SELECT id FROM parts WHERE part_number=?", (p_num,))
                    existing = cursor.fetchone()
                    if existing:
                        part['id'] = existing[0]
                        created_parts[p_num] = existing[0]
                        continue

                cursor.execute("""
                    INSERT INTO parts (part_name, part_number, category, location, min_quantity, purchase_price, selling_price, quantity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                """, (
                    part['part_name'], part['part_number'], part.get('category', ''), 
                    part.get('location', ''), part.get('min_quantity', 5), 
                    part.get('purchase_price', 0), part.get('selling_price', 0)
                ))
                part['id'] = cursor.lastrowid # Assign new ID back
                if p_num:
                    created_parts[p_num] = part['id']

        # 2. Insert Bill
        cursor.execute("""
            INSERT INTO supplier_bills (bill_number, supplier_id, pdf_filename, total_amount, bill_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            bill_data['bill_number'], bill_data.get('supplier_id'), 
            bill_data.get('pdf_filename', ''), bill_data.get('total_amount', 0),
            bill_data.get('bill_date'), bill_data.get('notes', '')
        ))
        bill_id = cursor.lastrowid

        # 3. Insert Items & Update Stock
        for item in items_data:
            part_id = item['part_id']
            if isinstance(part_id, dict):
                part_id = part_id.get('id')
            qty = item['quantity']
            
            # If part was just created, it might be matched by a temporary dict reference.
            # Assuming the UI handles mapping new_parts_data IDs to items_data part_ids correctly.

            cursor.execute("""
                INSERT INTO supplier_bill_items (bill_id, part_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            """, (bill_id, part_id, qty, item.get('unit_price', 0)))

            # Increase stock and potentially update purchase price
            cursor.execute("""
                UPDATE parts 
                SET quantity = quantity + ?, purchase_price = ?
                WHERE id = ?
            """, (qty, item.get('unit_price', 0), part_id))

        conn.commit()
        return bill_id
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def save_customer_bill(bill_data, items_data):
    """
    Saves a customer bill and DECREASES stock.
    Blocks if stock is insufficient.
    """
    conn = get_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    try:
        # 1. Validate Stock
        for item in items_data:
            part_id = item['part_id']
            qty = item['quantity']
            cursor.execute("SELECT part_name, part_number, quantity FROM parts WHERE id=?", (part_id,))
            part_info = cursor.fetchone()
            if not part_info:
                raise ValueError(f"Part ID {part_id} not found in database.")
            
            if part_info['quantity'] < qty:
                raise ValueError(f"Insufficient stock for {part_info['part_name']} ({part_info['part_number']}). "
                                 f"Requested: {qty}, Available: {part_info['quantity']}")

        # 2. Insert Bill
        cursor.execute("""
            INSERT INTO customer_bills (bill_number, customer_name, customer_phone, customer_id, pdf_filename, total_amount, discount, bill_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bill_data['bill_number'], bill_data.get('customer_name', ''), 
            bill_data.get('customer_phone', ''), bill_data.get('customer_id'),
            bill_data.get('pdf_filename', ''), bill_data.get('total_amount', 0),
            bill_data.get('discount', 0), bill_data.get('bill_date'), bill_data.get('notes', '')
        ))
        bill_id = cursor.lastrowid

        # 3. Insert Items & Update Stock
        for item in items_data:
            part_id = item['part_id']
            qty = item['quantity']
            
            cursor.execute("""
                INSERT INTO customer_bill_items (bill_id, part_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            """, (bill_id, part_id, qty, item.get('unit_price', 0)))

            # Decrease stock
            cursor.execute("""
                UPDATE parts 
                SET quantity = quantity - ?
                WHERE id = ?
            """, (qty, part_id))

        conn.commit()
        return bill_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# --- Reporting & Dashboard ---

def get_dashboard_stats():
    stats = {}
    stats['total_parts'] = execute_query("SELECT COUNT(*) as c FROM parts", fetchone=True)['c']
    stats['total_value'] = execute_query("SELECT SUM(quantity * purchase_price) as v FROM parts", fetchone=True)['v'] or 0
    stats['low_stock'] = execute_query("SELECT COUNT(*) as c FROM parts WHERE quantity <= min_quantity", fetchone=True)['c']
    
    # Processed today
    sup_today = execute_query("SELECT COUNT(*) as c FROM supplier_bills WHERE date(bill_date) = date('now', 'localtime')", fetchone=True)['c']
    cust_today = execute_query("SELECT COUNT(*) as c FROM customer_bills WHERE date(bill_date) = date('now', 'localtime')", fetchone=True)['c']
    stats['bills_today'] = sup_today + cust_today
    
    return stats

def get_low_stock_parts():
    return execute_query("SELECT * FROM parts WHERE quantity <= min_quantity ORDER BY quantity ASC", fetchall=True)

def get_recent_bills(limit=10):
    query = """
        SELECT id, bill_number, total_amount, bill_date, 'Supplier' as type FROM supplier_bills
        UNION ALL
        SELECT id, bill_number, total_amount, bill_date, 'Customer' as type FROM customer_bills
        ORDER BY bill_date DESC LIMIT ?
    """
    return execute_query(query, (limit,), fetchall=True)

def get_sales_over_time(days=30):
    query = """
        SELECT date(bill_date) as bdate, SUM(total_amount) as total
        FROM customer_bills
        WHERE status != 'Voided' AND bill_date >= date('now', ?)
        GROUP BY date(bill_date)
        ORDER BY date(bill_date) ASC
    """
    return execute_query(query, (f"-{days} days",), fetchall=True)

def get_all_supplier_bills():
    query = """
        SELECT b.*, s.name as supplier_name 
        FROM supplier_bills b
        LEFT JOIN suppliers s ON b.supplier_id = s.id
        ORDER BY b.bill_date DESC
    """
    return execute_query(query, fetchall=True)

def get_all_customer_bills():
    query = "SELECT * FROM customer_bills ORDER BY bill_date DESC"
    return execute_query(query, fetchall=True)

def get_next_customer_bill_number():
    res = execute_query("SELECT COUNT(*) as c FROM customer_bills", fetchone=True)
    count = res['c'] + 1
    return f"CB-{1000 + count}"

def void_customer_bill(bill_id):
    """
    Voids a customer bill and returns the stock of items back to the inventory.
    """
    conn = get_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    try:
        # Check current status
        cursor.execute("SELECT status FROM customer_bills WHERE id=?", (bill_id,))
        bill = cursor.fetchone()
        if not bill:
            raise ValueError("Bill not found.")
        if bill['status'] == 'Voided':
            raise ValueError("Bill is already voided.")
            
        # Get items
        cursor.execute("SELECT part_id, quantity FROM customer_bill_items WHERE bill_id=?", (bill_id,))
        items = cursor.fetchall()
        
        # Restore stock
        for item in items:
            part_id = item['part_id']
            qty = item['quantity']
            cursor.execute("UPDATE parts SET quantity = quantity + ? WHERE id = ?", (qty, part_id))
            
        # Update status
        cursor.execute("UPDATE customer_bills SET status = 'Voided' WHERE id = ?", (bill_id,))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
