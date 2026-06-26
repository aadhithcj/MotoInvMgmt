import sqlite3
import random
from database.connection import get_connection, init_db
from database.models import add_part, add_supplier, add_customer, get_all_parts, get_all_customers, get_all_suppliers

def populate():
    # Ensure DB is initialized perfectly
    init_db()

    # 1. Add Suppliers
    suppliers = [
        {'name': 'Yamaha Genuine Parts', 'phone': '9876543210', 'address': '123 Factory Road, Delhi'},
        {'name': 'Castrol Distributors', 'phone': '9988776655', 'address': 'Industrial Area, Mumbai'},
        {'name': 'Motul Auto India', 'phone': '9123456780', 'address': 'Tech Park, Bangalore'}
    ]
    for s in suppliers:
        try: add_supplier(s)
        except: pass
        
    # 2. Add Customers
    customers = [
        {'name': 'Raj Kumar', 'phone': '8877665544', 'email': 'raj@example.com', 'address': 'Delhi'},
        {'name': 'Suresh Singh', 'phone': '7788990011', 'email': '', 'address': 'Noida'},
        {'name': 'Amit Verma', 'phone': '9988001122', 'email': 'amit@example.com', 'address': 'Gurgaon'}
    ]
    for c in customers:
        try: add_customer(c)
        except: pass

    # 3. Add Parts
    parts = [
        {'part_name': 'Motul 7100 10W50', 'part_number': 'MTL-7100', 'category': 'Oil', 'location': 'A1', 'min_quantity': 10, 'purchase_price': 800, 'selling_price': 950, 'quantity': 50},
        {'part_name': 'Castrol Activ 4T', 'part_number': 'CST-ACT4T', 'category': 'Oil', 'location': 'A2', 'min_quantity': 15, 'purchase_price': 350, 'selling_price': 420, 'quantity': 60},
        {'part_name': 'Yamaha R15 Brake Pad', 'part_number': 'YMH-R15-BP', 'category': 'Brakes', 'location': 'B1', 'min_quantity': 5, 'purchase_price': 400, 'selling_price': 550, 'quantity': 20},
        {'part_name': 'KTM Duke Chain Sprocket', 'part_number': 'KTM-CS-390', 'category': 'Drivetrain', 'location': 'C1', 'min_quantity': 2, 'purchase_price': 2500, 'selling_price': 3200, 'quantity': 5},
        {'part_name': 'NGK Spark Plug', 'part_number': 'NGK-CR8E', 'category': 'Engine', 'location': 'D1', 'min_quantity': 20, 'purchase_price': 150, 'selling_price': 200, 'quantity': 100}
    ]
    for p in parts:
        try: add_part(p)
        except: pass

    print("Database populated successfully with Parts, Suppliers, and Customers!")

if __name__ == '__main__':
    populate()
