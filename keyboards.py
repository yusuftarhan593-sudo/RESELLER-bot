from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍️ Ürünler"), KeyboardButton(text="💰 Bakiyem")],
        [KeyboardButton(text="📋 Siparişlerim"), KeyboardButton(text="👤 Hesabım")]
    ], resize_keyboard=True)

def categories_keyboard(categories):
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(text=f"{cat[2]} {cat[1]}", callback_data=f"cat_{cat[0]}")])
    buttons.append([InlineKeyboardButton(text="🔙 Geri", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def products_keyboard(products, category_id):
    buttons = []
    for p in products:
        buttons.append([InlineKeyboardButton(text=f"{p[2]}", callback_data=f"product_{p[0]}")])
    buttons.append([InlineKeyboardButton(text="🔙 Kategoriler", callback_data="back_categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def period_keyboard(product_id, price_daily, price_weekly, price_monthly):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📅 Günlük - {price_daily}₺", callback_data=f"buy_{product_id}_daily")],
        [InlineKeyboardButton(text=f"📅 Haftalık - {price_weekly}₺", callback_data=f"buy_{product_id}_weekly")],
        [InlineKeyboardButton(text=f"📅 Aylık - {price_monthly}₺", callback_data=f"buy_{product_id}_monthly")],
        [InlineKeyboardButton(text="🔙 Geri", callback_data="back_categories")]
    ])

def confirm_buy_keyboard(product_id, period):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Onayla", callback_data=f"confirm_{product_id}_{period}"),
         InlineKeyboardButton(text="❌ İptal", callback_data="back_categories")]
    ])

def balance_menu_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Satın Alım Geçmişi", callback_data=f"order_history_{user_id}")],
        [InlineKeyboardButton(text="💳 Yükleme Geçmişi", callback_data=f"topup_history_{user_id}")]
    ])

def admin_inline_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📂 Kategori Ekle", callback_data="admin_add_category"),
         InlineKeyboardButton(text="📦 Ürün Ekle", callback_data="admin_add_product")],
        [InlineKeyboardButton(text="🔑 Stok Ekle", callback_data="admin_add_stock"),
         InlineKeyboardButton(text="💵 Bakiye Ekle", callback_data="admin_add_balance")],
        [InlineKeyboardButton(text="👥 Kullanıcı Ara", callback_data="admin_search_user"),
         InlineKeyboardButton(text="📊 İstatistikler", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📋 Tüm Siparişler", callback_data="admin_all_orders")]
    ])

def user_detail_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 Bakiye Ekle", callback_data=f"bal_add_{user_id}"),
         InlineKeyboardButton(text="💲 Özel Fiyat", callback_data=f"custom_price_{user_id}")],
        [InlineKeyboardButton(text="📋 Satın Alım Geçmişi", callback_data=f"order_history_{user_id}")],
        [InlineKeyboardButton(text="🔙 Geri", callback_data="admin_search_user")]
    ])

def custom_price_products_keyboard(products, user_id):
    buttons = []
    for p in products:
        buttons.append([InlineKeyboardButton(
            text=f"{p[2]}",
            callback_data=f"set_custom_{user_id}_{p[0]}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 Geri", callback_data=f"user_detail_{user_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📂 Kategori Yönetimi"), KeyboardButton(text="📦 Ürün Yönetimi")],
        [KeyboardButton(text="🔑 Stok Ekle"), KeyboardButton(text="👥 Kullanıcılar")],
        [KeyboardButton(text="💵 Bakiye Yükle"), KeyboardButton(text="📊 İstatistikler")],
        [KeyboardButton(text="📋 Tüm Siparişler"), KeyboardButton(text="🔙 Kullanıcı Modu")]
    ], resize_keyboard=True)

def cancel_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="❌ İptal")]
    ], resize_keyboard=True)
