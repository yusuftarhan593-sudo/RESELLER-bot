from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍️ Buy keys")],
        [KeyboardButton(text="🏛️ Account"), KeyboardButton(text="🚀 Log out")]
    ], resize_keyboard=True)

def categories_keyboard(categories):
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(text=str(cat[2]) + " " + str(cat[1]), callback_data="cat_" + str(cat[0]))])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def products_keyboard(products, category_id):
    buttons = []
    for p in products:
        buttons.append([InlineKeyboardButton(text=str(p[2]), callback_data="product_" + str(p[0]))])
    buttons.append([InlineKeyboardButton(text="⬅️ Go back", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def period_select_keyboard(product_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 day", callback_data="period_" + str(product_id) + "_daily")],
        [InlineKeyboardButton(text="7 day", callback_data="period_" + str(product_id) + "_weekly")],
        [InlineKeyboardButton(text="30 day", callback_data="period_" + str(product_id) + "_monthly")],
        [InlineKeyboardButton(text="⬅️ Go back", callback_data="back_main")]
    ])

def buy_keyboard(product_id, period):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Buy", callback_data="buyone_" + str(product_id) + "_" + str(period))],
        [InlineKeyboardButton(text="⬅️ Go back", callback_data="product_" + str(product_id))]
    ])

def confirm_buy_keyboard(product_id, period, amount):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data="confirm_" + str(product_id) + "_" + str(period) + "_" + str(amount)),
         InlineKeyboardButton(text="❌ Cancel", callback_data="back_main")]
    ])

def balance_menu_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Purchase History", callback_data="order_history_" + str(user_id))],
        [InlineKeyboardButton(text="💳 Top-up History", callback_data="topup_history_" + str(user_id))]
    ])

def admin_inline_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📂 Kategori Ekle", callback_data="admin_add_category"),
         InlineKeyboardButton(text="📦 Urun Ekle", callback_data="admin_add_product")],
        [InlineKeyboardButton(text="🔑 Stok Ekle", callback_data="admin_add_stock"),
         InlineKeyboardButton(text="💵 Bakiye Ekle", callback_data="admin_add_balance")],
        [InlineKeyboardButton(text="👥 Kullanici Ekle", callback_data="admin_add_user"),
         InlineKeyboardButton(text="🔍 Kullanicilar", callback_data="admin_search_user")],
        [InlineKeyboardButton(text="📊 Istatistikler", callback_data="admin_stats"),
         InlineKeyboardButton(text="📋 Tum Siparisler", callback_data="admin_all_orders")],
        [InlineKeyboardButton(text="📂 Kategori Yonet", callback_data="admin_manage_categories"),
         InlineKeyboardButton(text="📦 Urun Yonet", callback_data="admin_manage_products")]
    ])

def user_detail_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 Bakiye Ekle", callback_data="bal_select_" + str(user_id)),
         InlineKeyboardButton(text="💸 Bakiye Dus", callback_data="bal_remove_" + str(user_id))],
        [InlineKeyboardButton(text="💲 Ozel Fiyat", callback_data="custom_price_" + str(user_id)),
         InlineKeyboardButton(text="🔑 Sifre Degistir", callback_data="change_pass_" + str(user_id))],
        [InlineKeyboardButton(text="📋 Satin Alim Gecmisi", callback_data="order_history_" + str(user_id))],
        [InlineKeyboardButton(text="🗑 Kullanici Sil", callback_data="delete_user_" + str(user_id))],
        [InlineKeyboardButton(text="🔙 Geri", callback_data="admin_search_user")]
    ])

def users_list_keyboard(users, prefix="detail"):
    buttons = []
    for u in users:
        if prefix == "bal":
            cb = "bal_select_" + str(u[0])
        elif prefix == "bal_remove":
            cb = "bal_remove_" + str(u[0])
        else:
            cb = "admin_user_" + str(u[0])
        buttons.append([InlineKeyboardButton(
            text="👤 " + str(u[1]) + " | 💰 " + str(u[3]) + "$",
            callback_data=cb
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def categories_manage_keyboard(categories):
    buttons = []
    for cat in categories:
        buttons.append([
            InlineKeyboardButton(text=str(cat[2]) + " " + str(cat[1]), callback_data="admin_cat_detail_" + str(cat[0])),
            InlineKeyboardButton(text="✏️", callback_data="edit_cat_" + str(cat[0])),
            InlineKeyboardButton(text="🗑", callback_data="delete_cat_" + str(cat[0]))
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Geri", callback_data="back_admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def products_manage_keyboard(products):
    buttons = []
    for p in products:
        buttons.append([
            InlineKeyboardButton(text=str(p[2]), callback_data="admin_prod_detail_" + str(p[0])),
            InlineKeyboardButton(text="✏️", callback_data="edit_product_" + str(p[0])),
            InlineKeyboardButton(text="🗑", callback_data="delete_product_" + str(p[0]))
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Geri", callback_data="back_admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def custom_price_products_keyboard(products, user_id):
    buttons = []
    for p in products:
        buttons.append([InlineKeyboardButton(
            text=str(p[2]),
            callback_data="set_custom_" + str(user_id) + "_" + str(p[0])
        )])
    buttons.append([InlineKeyboardButton(text="🔙 Geri", callback_data="admin_search_user")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def stats_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Gunluk", callback_data="stats_daily"),
         InlineKeyboardButton(text="📅 Haftalik", callback_data="stats_weekly")],
        [InlineKeyboardButton(text="📅 Aylik", callback_data="stats_monthly")],
        [InlineKeyboardButton(text="🗑 Sifirla", callback_data="stats_reset")]
    ])

def cancel_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Cancel")]
    ], resize_keyboard=True)

def stock_period_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 1 Day Stock", callback_data="stock_period_daily")],
        [InlineKeyboardButton(text="📅 7 Day Stock", callback_data="stock_period_weekly")],
        [InlineKeyboardButton(text="📅 30 Day Stock", callback_data="stock_period_monthly")]
    ])
