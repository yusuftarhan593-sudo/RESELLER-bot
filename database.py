def get_user_orders(user_id):
    # Kullanıcının satın alım geçmişini döndür
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    orders = cursor.fetchall()
    conn.close()
    return orders

def set_custom_price(user_id, product_id, price):
    # Kişiye özel fiyat kaydet
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO custom_prices (user_id, product_id, price)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, product_id) DO UPDATE SET price = excluded.price
    """, (user_id, product_id, price))
    conn.commit()
    conn.close()
