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
        buttons.append([InlineKeyboardButton(text=f"{p[2]} - {p[4]}₺", callback_data=f"product_{p[0]}")])
    buttons.append([InlineKeyboardButton(text="🔙 Kategoriler", callback_data="back_categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def product_detail_keyboard(product_id, category_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Satın Al", callback_data=f"buy_{product_id}")],
        [InlineKeyboardButton(text="🔙 Geri", callback_data=f"cat_{category_id}")]
    ])

def confirm_buy_keyboard(product_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Onayla", callback_data=f"confirm_buy_{product_id}"),
         InlineKeyboardButton(text="❌ İptal", callback_data="back_categories")]
    ])

def admin_main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📂 Kategori Yönetimi"), KeyboardButton(text="📦 Ürün Yönetimi")],
        [KeyboardButton(text="🔑 Stok Ekle"), KeyboardButton(text="👥 Kullanıcılar")],
        [KeyboardButton(text="💵 Bakiye Yükle"), KeyboardButton(text="📊 İstatistikler")],
        [KeyboardButton(text="📋 Tüm Siparişler"), KeyboardButton(text="🔙 Kullanıcı Modu")]
    ], resize_keyboard=True)

def category_manage_keyboard(categories):
    buttons = []
    for cat in categories:
        buttons.append([
            InlineKeyboardButton(text=f"{cat[2]} {cat[1]}", callback_data=f"admin_cat_{cat[0]}"),
            InlineKeyboardButton(text="✏️", callback_data=f"edit_cat_{cat[0]}"),
            InlineKeyboardButton(text="🗑️", callback_data=f"del_cat_{cat[0]}")
        ])
    buttons.append([InlineKeyboardButton(text="➕ Yeni Kategori", callback_data="add_category")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def product_manage_keyboard(products):
    buttons = []
    for p in products:
        stock_count = p[7] if len(p) > 7 else 0
        buttons.append([
            InlineKeyboardButton(text=f"{p[2]} ({stock_count} stok)", callback_data=f"admin_product_{p[0]}"),
            InlineKeyboardButton(text="💲", callback_data=f"edit_price_{p[0]}"),
            InlineKeyboardButton(text="🗑️", callback_data=f"del_product_{p[0]}")
        ])
    buttons.append([InlineKeyboardButton(text="➕ Yeni Ürün", callback_data="add_product")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def stats_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Günlük", callback_data="stats_daily"),
         InlineKeyboardButton(text="📅 Haftalık", callback_data="stats_weekly")],
        [InlineKeyboardButton(text="📅 Aylık", callback_data="stats_monthly"),
         InlineKeyboardButton(text="📅 Yıllık", callback_data="stats_yearly")]
    ])

def cancel_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="❌ İptal")]
    ], resize_keyboard=True)
