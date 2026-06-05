import sqlite3
import hashlib

DB_NAME = "/app/data/bot.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        balance REAL DEFAULT 0,
        language TEXT DEFAULT 'en',
        is_banned INTEGER DEFAULT 0,
        telegram_id INTEGER DEFAULT NULL,
        created_at TEXT DEFAULT (datetime('now')))""")
    c.execute("""CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, emoji TEXT DEFAULT '', is_active INTEGER DEFAULT 1)""")
    c.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, category_id INTEGER,
        name TEXT NOT NULL, description TEXT,
        price_daily REAL DEFAULT 0,
        price_weekly REAL DEFAULT 0,
        price_monthly REAL DEFAULT 0,
        cost_daily REAL DEFAULT 0,
        cost_weekly REAL DEFAULT 0,
        cost_monthly REAL DEFAULT 0,
        is_active INTEGER DEFAULT 1)""")
    c.execute("""CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER,
        key_code TEXT NOT NULL, is_sold INTEGER DEFAULT 0,
        period TEXT DEFAULT 'daily',
        sold_to INTEGER DEFAULT NULL, sold_at TEXT DEFAULT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        product_id INTEGER, product_name TEXT, key_code TEXT,
        price REAL, period TEXT, created_at TEXT DEFAULT (datetime('now')))""")
    c.execute("""CREATE TABLE IF NOT EXISTS balance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        amount REAL, note TEXT, added_by INTEGER,
        created_at TEXT DEFAULT (datetime('now')))""")
    c.execute("""CREATE TABLE IF NOT EXISTS custom_prices (
        user_id INTEGER, product_id INTEGER,
        price_daily REAL, price_weekly REAL, price_monthly REAL,
        PRIMARY KEY (user_id, product_id))""")
    conn.commit()
    conn.close()

def add_user_by_admin(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return False
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
              (username, hash_password(password)))
    conn.commit()
    conn.close()
    return True

def delete_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

def change_user_password(user_id, new_password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE id=?", (hash_password(new_password), user_id))
    conn.commit()
    conn.close()

def login_user(username, password, telegram_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    user = c.fetchone()
    if user:
        c.execute("UPDATE users SET telegram_id=? WHERE username=?", (telegram_id, username))
        conn.commit()
    conn.close()
    return user

def get_user_by_telegram(telegram_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = c.fetchall()
    conn.close()
    return users

def get_balance(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def add_balance(user_id, amount, added_by, note="Manual top-up"):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, user_id))
    c.execute("INSERT INTO balance_logs (user_id, amount, note, added_by) VALUES (?, ?, ?, ?)",
              (user_id, amount, note, added_by))
    conn.commit()
    conn.close()

def remove_balance(user_id, amount, added_by, note="Manuel dusurme"):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance - ? WHERE id=?", (amount, user_id))
    c.execute("INSERT INTO balance_logs (user_id, amount, note, added_by) VALUES (?, ?, ?, ?)",
              (user_id, -amount, note, added_by))
    conn.commit()
    conn.close()

def get_categories():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM categories WHERE is_active=1")
    cats = c.fetchall()
    conn.close()
    return cats

def get_category_by_id(category_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM categories WHERE id=?", (category_id,))
    cat = c.fetchone()
    conn.close()
    return cat

def add_category(name, emoji=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO categories (name, emoji) VALUES (?, ?)", (name, emoji))
    conn.commit()
    conn.close()

def delete_category(category_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE categories SET is_active=0 WHERE id=?", (category_id,))
    conn.commit()
    conn.close()

def update_category(category_id, name, emoji):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE categories SET name=?, emoji=? WHERE id=?", (name, emoji, category_id))
    conn.commit()
    conn.close()

def get_products(category_id=None):
    conn = get_conn()
    c = conn.cursor()
    if category_id:
        c.execute("SELECT * FROM products WHERE category_id=? AND is_active=1", (category_id,))
    else:
        c.execute("SELECT * FROM products WHERE is_active=1")
    products = c.fetchall()
    conn.close()
    return products

def get_product(product_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id=?", (product_id,))
    product = c.fetchone()
    conn.close()
    return product

def delete_product(product_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE products SET is_active=0 WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

def update_product_prices(product_id, price_daily, price_weekly, price_monthly, cost_daily, cost_weekly, cost_monthly):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""UPDATE products SET price_daily=?, price_weekly=?, price_monthly=?,
        cost_daily=?, cost_weekly=?, cost_monthly=? WHERE id=?""",
              (price_daily, price_weekly, price_monthly, cost_daily, cost_weekly, cost_monthly, product_id))
    conn.commit()
    conn.close()

def add_product(category_id, name, description, price_daily, price_weekly, price_monthly, cost_daily, cost_weekly, cost_monthly):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO products (category_id, name, description, price_daily, price_weekly, price_monthly, cost_daily, cost_weekly, cost_monthly) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (category_id, name, description, price_daily, price_weekly, price_monthly, cost_daily, cost_weekly, cost_monthly))
    conn.commit()
    conn.close()

def get_stock_count(product_id, period=None):
    conn = get_conn()
    c = conn.cursor()
    if period:
        c.execute("SELECT COUNT(*) FROM stock WHERE product_id=? AND is_sold=0 AND period=?", (product_id, period))
    else:
        c.execute("SELECT COUNT(*) FROM stock WHERE product_id=? AND is_sold=0", (product_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def add_stock_with_period(product_id, key_code, period):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO stock (product_id, key_code, period) VALUES (?, ?, ?)", (product_id, key_code, period))
    conn.commit()
    conn.close()

def get_custom_prices(user_id, product_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT price_daily, price_weekly, price_monthly FROM custom_prices WHERE user_id=? AND product_id=?",
              (user_id, product_id))
    row = c.fetchone()
    conn.close()
    return row

def set_custom_prices(user_id, product_id, price_daily, price_weekly, price_monthly):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO custom_prices (user_id, product_id, price_daily, price_weekly, price_monthly)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, product_id) DO UPDATE SET
        price_daily=excluded.price_daily,
        price_weekly=excluded.price_weekly,
        price_monthly=excluded.price_monthly""",
              (user_id, product_id, price_daily, price_weekly, price_monthly))
    conn.commit()
    conn.close()

def buy_product(user_id, product_id, period):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM stock WHERE product_id=? AND is_sold=0 AND period=? LIMIT 1", (product_id, period))
    stock = c.fetchone()
    if not stock:
        conn.close()
        return None
    product = get_product(product_id)
    custom = get_custom_prices(user_id, product_id)
    if period == "daily":
        price = custom[0] if custom else product[4]
    elif period == "weekly":
        price = custom[1] if custom else product[5]
    else:
        price = custom[2] if custom else product[6]
    balance = get_balance(user_id)
    if balance < price:
        conn.close()
        return False
    c.execute("UPDATE users SET balance = balance - ? WHERE id=?", (price, user_id))
    c.execute("UPDATE stock SET is_sold=1, sold_to=?, sold_at=datetime('now') WHERE id=?",
              (user_id, stock[0]))
    c.execute("INSERT INTO orders (user_id, product_id, product_name, key_code, price, period) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, product_id, product[2], stock[2], price, period))
    conn.commit()
    conn.close()
    return stock[2]

def get_user_orders(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    orders = c.fetchall()
    conn.close()
    return orders

def get_all_orders():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 50")
    orders = c.fetchall()
    conn.close()
    return orders

def get_stats(period):
    conn = get_conn()
    c = conn.cursor()
    if period == "daily":
        date_filter = "date(o.created_at) = date('now')"
        cost_col = "p.cost_daily"
    elif period == "weekly":
        date_filter = "o.created_at >= datetime('now', '-7 days')"
        cost_col = "p.cost_weekly"
    else:
        date_filter = "o.created_at >= datetime('now', '-30 days')"
        cost_col = "p.cost_monthly"
    c.execute("SELECT COUNT(*), SUM(price) FROM orders o WHERE " + date_filter)
    row = c.fetchone()
    total_orders = row[0] or 0
    total_revenue = round(row[1] or 0, 2)
    c.execute("SELECT SUM(" + cost_col + ") FROM orders o JOIN products p ON o.product_id = p.id WHERE " + date_filter)
    cost_row = c.fetchone()
    total_cost = round(cost_row[0] or 0, 2)
    net_profit = round(total_revenue - total_cost, 2)
    conn.close()
    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "net_profit": net_profit
    }
