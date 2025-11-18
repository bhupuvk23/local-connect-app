# models.py
import json
from db import get_conn

# USERS
def create_user(username, password, role, display_name=None):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO users (username, password, role, display_name) VALUES (?, ?, ?, ?)',
                    (username, password, role, display_name))
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        print('create_user error', e)
        return None
    finally:
        conn.close()

def authenticate(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

# PRODUCTS
def add_product(vendor_id, title, description, price, category, image_path):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('INSERT INTO products (vendor_id, title, description, price, category, image_path) VALUES (?, ?, ?, ?, ?, ?)',
                (vendor_id, title, description, price, category, image_path))
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid

def get_products(category=None):
    conn = get_conn()
    cur = conn.cursor()
    if category:
        cur.execute('SELECT p.*, u.display_name as vendor_name FROM products p LEFT JOIN users u ON p.vendor_id=u.id WHERE category=?', (category,))
    else:
        cur.execute('SELECT p.*, u.display_name as vendor_name FROM products p LEFT JOIN users u ON p.vendor_id=u.id')
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ORDERS
def place_order(customer_id, vendor_id, items, total, firebase_key=None):
    conn = get_conn()
    cur = conn.cursor()
    items_json = json.dumps(items)
    cur.execute('INSERT INTO orders (customer_id, vendor_id, items_json, total, firebase_key) VALUES (?, ?, ?, ?, ?)',
                (customer_id, vendor_id, items_json, total, firebase_key))
    conn.commit()
    oid = cur.lastrowid
    conn.close()
    return oid

def get_orders_for_vendor(vendor_id, since_id=0):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM orders WHERE vendor_id=? AND id>? ORDER BY created_at DESC', (vendor_id, since_id))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_order_status(order_id, status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('UPDATE orders SET status=? WHERE id=?', (status, order_id))
    conn.commit()
    conn.close()
