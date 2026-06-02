import sqlite3
import os
from datetime import datetime

DB_NAME = "bot.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        balance REAL DEFAULT 0,
        custom_discount REAL DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        emoji TEXT DEFAULT ''
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        price REAL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        key_code TEXT NOT NULL,
        is_sold INTEGER DEFAULT 0,
        sold_to INTEGER DEFAULT NULL,
        sold_at TEXT DEFAULT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        product_name TEXT,
        key_code TEXT,
        price REAL,
        created_at TEXT DEFAULT (datetime('now'))
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS balance_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        note TEXT,
        added_by INTEGER,
        created_at TEXT DEFAULT (datetime('now'))
    )""")
    conn.commit()
    conn.close()

def get_or_create_user(user_id, username, full_name):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    if not user:
        c.execute("INSERT INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
                  (user_id, username, full_name))
        conn.commit()
    conn.close()
    return user
