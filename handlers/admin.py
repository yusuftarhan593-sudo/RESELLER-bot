from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
import os
import sqlite3

router = Router()
ADMIN_IDS = [int(os.environ.get("ADMIN_ID", 0))]

def is_admin(user_id):
    return user_id in ADMIN_IDS

class AddCategory(StatesGroup):
    name = State()
    emoji = State()

class EditCategory(StatesGroup):
    category_id = State()
    name = State()
    emoji = State()

class AddProduct(StatesGroup):
    category_id = State()
    name = State()
    description = State()
    price_daily = State()
    price_weekly = State()
    price_monthly = State()
    cost_daily = State()
    cost_weekly = State()
    cost_monthly = State()

class EditProduct(StatesGroup):
    product_id = State()
    price_daily = State()
    price_weekly = State()
    price_monthly = State()
    cost_daily = State()
    cost_weekly = State()
    cost_monthly = State()

class AddStock(StatesGroup):
    product_id = State()
    period = State()
    keys = State()

class AddBalance(StatesGroup):
    user_id = State()
    amount = State()

class RemoveBalance(StatesGroup):
    user_id = State()
    amount = State()

class AddUser(StatesGroup):
    username = State()
    password = State()

class ChangePassword(StatesGroup):
    user_id = State()
    password = State()

class CustomPrice(StatesGroup):
    user_id = State()
    product_id = State()
    price_daily = State()
    price_weekly = State()
    price_monthly = State()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Yetkisiz erisim!")
        return
    await message.answer("Admin Paneli\nNe yapmak istersiniz?", reply_markup=kb.admin_inline_menu())

@router.callback_query(F.data == "back_admin")
async def back_admin(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    try:
        await callback.message.edit_text("Admin Paneli\nNe yapmak istersiniz?", reply_markup=kb.admin_inline_menu())
    except:
        await callback.message.answer("Admin Paneli\nNe yapmak istersiniz?", reply_markup=kb.admin_inline_menu())
    await callback.answer()

@router.callback_query(F.data == "admin_add_category")
async def cb_add_category(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    try:
        await callback.message.edit_text("Kategori adini girin:")
    except:
        await callback.message.answer("Kategori adini girin:")
    await callback.message.answer("Kategori adini girin:", reply_markup=kb.cancel_keyboard())
    await state.set_state(AddCategory.name)
    await callback.answer()

@router.message(AddCategory.name)
async def add_category_name(message: Message, state: FSMContext):
    if message.text == "Cancel":
        await state.clear()
        await message.answer("Iptal edildi.")
        return
    await state.update_data(name=message.text)
    await message.answer("Emoji girin (- yazin atlamak icin):")
    await state.set_state(AddCategory.emoji)

@router.message(AddCategory.emoji)
async def add_category_emoji(message: Message, state: FSMContext):
    data = await state.get_data()
    emoji = message.text if message.text != "-" else ""
    db.add_category(data["name"], emoji)
    await message.answer("Kategori eklendi: " + data["name"])
    await state.clear()

@router.callback_query(F.data == "admin_manage_categories")
async def manage_categories(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    categories = db.get_categories()
    if not categories:
        await callback.answer("Hic kategori yok.", show_alert=True)
        return
    try:
        await callback.message.edit_text("Kategoriler:", reply_markup=kb.categories_manage_keyboard(categories))
    except:
        await callback.message.answer("Kategoriler:", reply_markup=kb.categories_manage_keyboard(categories))
    await callback.answer()

@router.callback_query(F.data.startswith("delete_cat_"))
async def delete_category(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    cat_id = int(callback.data.split("_")[2])
    db.delete_category(cat_id)
    await callback.answer("Kategori silindi!", show_alert=True)

@router.callback_query(F.data.startswith("edit_cat_"))
async def edit_category_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    cat_id = int(callback.data.split("_")[2])
    await state.update_data(category_id=cat_id)
    try:
        await callback.message.edit_text("Yeni kategori adini girin:")
    except:
        await callback.message.answer("Yeni kategori adini girin:", reply_markup=kb.cancel_keyboard())
    await state.set_state(EditCategory.name)
    await callback.answer()

@router.message(EditCategory.name)
async def edit_category_name(message: Message, state: FSMContext):
    if message.text == "Cancel":
        await state.clear()
        await message.answer("Iptal edildi.")
        return
    await state.update_data(name=message.text)
    await message.answer("Yeni emoji girin (- yazin atlamak icin):")
    await state.set_state(EditCategory.emoji)

@router.message(EditCategory.emoji)
async def edit_category_emoji(message: Message, state: FSMContext):
    data = await state.get_data()
    emoji = message.text if message.text != "-" else ""
    db.update_category(data["category_id"], data["name"], emoji)
    await message.answer("Kategori guncellendi!")
    await state.clear()

@router.callback_query(F.data == "admin_manage_products")
async def manage_products(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    products = db.get_products()
    if not products:
        await callback.answer("Hic urun yok.", show_alert=True)
        return
    try:
        await callback.message.edit_text("Urunler:", reply_markup=kb.products_manage_keyboard(products))
    except:
        await callback.message.answer("Urunler:", reply_markup=kb.products_manage_keyboard(products))
    await callback.answer()

@router.callback_query(F.data.startswith("delete_product_"))
async def delete_product(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    product_id = int(callback.data.split("_")[2])
    db.delete_product(product_id)
    await callback.answer("Urun silindi!", show_alert=True)

@router.callback_query(F.data.startswith("edit_product_"))
async def edit_product_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    product_id = int(callback.data.split("_")[2])
    product = db.get_product(product_id)
    await state.update_data(product_id=product_id)
    text = (
        "Urun: " + str(product[2]) + "\n"
        "Mevcut:\n"
        "- Gunluk: " + str(product[4]) + "$\n"
        "- Haftalik: " + str(product[5]) + "$\n"
        "- Aylik: " + str(product[6]) + "$\n\n"
        "Yeni gunluk satis fiyati girin:"
    )
    try:
        await callback.message.edit_text(text)
    except:
        await callback.message.answer(text, reply_markup=kb.cancel_keyboard())
    await state.set_state(EditProduct.price_daily)
    await callback.answer()

@router.message(EditProduct.price_daily)
async def edit_price_daily(message: Message, state: FSMContext):
    if message.text == "Cancel":
        await state.clear()
        await message.answer("Iptal edildi.")
        return
    await state.update_data(price_daily=message.text.replace(",", ".").replace("$", ""))
    await message.answer("Yeni haftalik satis fiyati girin:")
    await state.set_state(EditProduct.price_weekly)

@router.message(EditProduct.price_weekly)
async def edit_price_weekly(message: Message, state: FSMContext):
    await state.update_data(price_weekly=message.text.replace(",", ".").replace("$", ""))
    await message.answer("Yeni aylik satis fiyati girin:")
    await state.set_state(EditProduct.price_monthly)

@router.message(EditProduct.price_monthly)
async def edit_price_monthly(message: Message, state: FSMContext):
    await state.update_data(price_monthly=message.text.replace(",", ".").replace("$", ""))
    await message.answer("Yeni gunluk MALIYET girin:")
    await state.set_state(EditProduct.cost_daily)

@router.message(EditProduct.cost_daily)
async def edit_cost_daily(message: Message, state: FSMContext):
    await state.update_data(cost_daily=message.text.replace(",", ".").replace("$", ""))
    await message.answer("Yeni haftalik MALIYET girin:")
    await state.set_state(EditProduct.cost_weekly)

@router.message(EditProduct.cost_weekly)
async def edit_cost_weekly(message: Message, state: FSMContext):
    await state.update_data(cost_weekly=message.text.replace(",", ".").replace("$", ""))
    await message.answer("Yeni aylik MALIYET girin:")
    await state.set_state(EditProduct.cost_monthly)

@router.message(EditProduct.cost_monthly)
async def edit_cost_monthly(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        db.update_product_prices(
            data["product_id"],
            float(data["price_daily"]), float(data["price_weekly"]), float(data["price_monthly"]),
            float(data["cost_daily"]), float(data["cost_weekly"]), float(message.text.replace(",", ".").replace("$", ""))
        )
        await message.answer("Urun guncellendi!")
    except Exception as e:
        await message.answer("Hata: " + str(e))
    await state.clear()

@router.callback_query(F.data == "admin_add_product")
async def cb_add_product(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    categories = db.get_categories()
    if not categories:
        await callback.answer("Once kategori ekleyin!", show_alert=True)
        return
    text = "Kategori ID secin:\n\n"
    for cat in categories:
        text += str(cat[0]) + " - " + str(cat[2]) + " " + str(cat[1]) + "\n"
    try:
        await callback.message.edit_text(text)
    except:
        await callback.message.answer(text, reply_markup=kb.cancel_keyboard())
    await state.set_state(AddProduct.category_id)
    await callback.answer()

@router.message(AddProduct.category_id)
async def add_product_cat(message: Message, state: FSMContext):
    if message.text == "Cancel":
        await state.clear()
        await message.answer("Iptal edildi.")
        return
    await state.update_data(category_id=message.text)
    await message.answer("Urun adini girin:")
    await state.set_state(AddProduct.name)

@router.message(AddProduct.name)
async def add_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Aciklama girin:")
    await state.set_state(AddProduct.description)

@router.message(AddProduct.description)
async def add_product_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Gunluk satis fiyati girin (ornek: 1.50):")
    await state.set_state(AddProduct.price_daily)

@router.message(AddProduct.price_daily)
async def add_product_price_daily(message: Message, state: FSMContext):
    await state.update_data(price_daily=message.text.replace(",", ".").replace("$", ""))
    await message.answer("Haftalik satis fiyati girin:")
    await state.set_state(AddProduct.price_weekly)

@router.message(AddProduct.price_weekly)
async def add_product_price_weekly(message: Message, state: FSMContext):
    await state.update_data(price_weekly=message.text.replace(",", ".").replace("$", ""))
    await message.answer("Aylik satis fiyati girin:")
    await state.set_state(AddProduct.price_monthly)

@router.message(AddProduct.price_monthly)
async def add_product_price_monthly(message: Message, state: FSMContext):
    await state.update_data(price_monthly=message.text.replace(",", ".").replace("$", ""))
    await message.answer("Gunluk MALIYET girin:")
    await state.set_state(AddProduct.cost_daily)

@router.message(AddProduct.cost_daily)
async def add_product_cost_daily(message: Message, state: FSMContext):
    await state.update_data(cost_daily=message.text.replace(",", ".").replace("$", ""))
    await message.answer("Haftalik MALIYET girin:")
    await state.set_state(AddProduct.cost_weekly)

@router.message(AddProduct.cost_weekly)
async def add_product_cost_weekly(message: Message, state: FSMContext):
    await state.update_data(cost_weekly=message.text.replace(",", ".").replace("$", ""))
    await message.answer("Aylik MALIYET girin:")
    await state.set_state(AddProduct.cost_monthly)

@router.message(AddProduct.cost_monthly)
async def add_product_cost_monthly(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        db.add_product(
            int(data["category_id"]), data["name"], data["description"],
            float(data["price_daily"]), float(data["price_weekly"]), float(data["price_monthly"]),
            float(data["cost_daily"]), float(data["cost_weekly"]), float(message.text.replace(",", ".").replace("$", ""))
        )
        await message.answer("Urun eklendi: " + data["name"])
    except Exception as e:
        await message.answer("Hata: " + str(e))
    await state.clear()

@router.callback_query(F.data == "admin_add_stock")
async def cb_add_stock(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    products = db.get_products()
    if not products:
        await callback.answer("Once urun ekleyin!", show_alert=True)
        return
    text = "Urun ID secin:\n\n"
    for p in products:
        text += str(p[0]) + " - " + str(p[2]) + "\n"
    try:
        await callback.message.edit_text(text)
    except:
        await callback.message.answer(text, reply_markup=kb.cancel_keyboard())
    await state.set_state(AddStock.product_id)
    await callback.answer()

@router.message(AddStock.product_id)
async def add_stock_product(message: Message, state: FSMContext):
    if message.text == "Cancel":
        await state.clear()
        await message.answer("Iptal edildi.")
        return
    await state.update_data(product_id=message.text)
    await message.answer("Hangi periyot icin stok ekleyeceksiniz?", reply_markup=kb.stock_period_keyboard())
    await state.set_state(AddStock.period)

@router.callback_query(F.data.startswith("addstock_"))
async def stock_period_select(callback: CallbackQuery, state: FSMContext):
    period = callback.data.replace("addstock_", "")
    await state.update_data(period=period)
    period_text = {"daily": "1 Gun", "weekly": "7 Gun", "monthly": "30 Gun"}[period]
    try:
        await callback.message.edit_text(
            "Periyot: " + period_text + "\n\nKey/kodlari girin (her satira bir tane):\n(Bitmek icin Cancel yazin)"
        )
    except:
        await callback.message.answer("Periyot: " + period_text + "\n\nKey/kodlari girin (her satira bir tane):\n(Bitmek icin Cancel yazin)")
    await state.set_state(AddStock.keys)
    await callback.answer()

@router.message(AddStock.keys)
async def add_stock_keys(message: Message, state: FSMContext):
    if message.text == "Cancel":
        await state.clear()
        await message.answer("Iptal edildi.")
        return
    data = await state.get_data()
    keys = message.text.strip().split("\n")
    for key in keys:
        db.add_stock_with_period(int(data["product_id"]), key.strip(), data["period"])
    await message.answer(
        str(len(keys)) + " adet stok eklendi! Periyot: " + data["period"] + "\n\nBaska periyot icin secin veya Cancel yazin:",
        reply_markup=kb.stock_period_keyboard()
    )
    await state.set_state(AddStock.period)

@router.callback_query(F.data == "admin_add_balance")
async def cb_add_balance(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    users = db.get_all_users()
    if not users:
        await callback.answer("Hic kullanici yok.", show_alert=True)
        return
    try:
        await callback.message.edit_text("Bakiye eklenecek kullaniciy secin:", reply_markup=kb.users_list_keyboard(users, "bal"))
    except:
        await callback.message.answer("Bakiye eklenecek kullaniciy secin:", reply_markup=kb.users_list_keyboard(users, "bal"))
    await callback.answer()

@router.callback_query(F.data.startswith("bal_select_"))
async def bal_select(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    user_id = int(callback.data.split("_")[2])
    await state.update_data(user_id=user_id)
    try:
        await callback.message.edit_text("Miktar girin (ornek: 50):")
    except:
        await callback.message.answer("Miktar girin (ornek: 50):", reply_markup=kb.cancel_keyboard())
    await state.set_state(AddBalance.amount)
    await callback.answer()

@router.message(AddBalance.amount)
async def add_balance_amount(message: Message, state: FSMContext):
    if message.text == "Cancel":
        await state.clear()
        await message.answer("Iptal edildi.")
        return
    data = await state.get_data()
    db.add_balance(int(data["user_id"]), float(message.text.replace(",", ".")), message.from_user.id)
    await message.answer("$" + message.text + " eklendi!")
    await state.clear()

@router.callback_query(F.data.startswith("bal_remove_"))
async def bal_remove(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    user_id = int(callback.data.split("_")[2])
    await state.update_data(user_id=user_id)
    try:
        await callback.message.edit_text("Dusurulecek miktari girin:")
    except:
        await callback.message.answer("Dusurulecek miktari girin:", reply_markup=kb.cancel_keyboard())
    await state.set_state(RemoveBalance.amount)
    await callback.answer()

@router.message(RemoveBalance.amount)
async def remove_balance_amount(message: Message, state: FSMContext):
    if message.text == "Cancel":
        await state.clear()
        await message.answer("Iptal edildi.")
        return
    data = await state.get_data()
    db.remove_balance(int(data["user_id"]), float(message.text.replace(",", ".")), message.from_user.id)
    await message.answer("$" + message.text + " dusuruldu!")
    await state.clear()

@router.callback_query(F.data == "admin_add_user")
async def cb_add_user(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    try:
        await callback.message.edit_text("Yeni kullanici adini girin:")
    except:
        await callback.message.answer("Yeni kullanici adini girin:", reply_markup=kb.cancel_keyboard())
    await state.set_state(AddUser.username)
    await callback.answer()

@router.message(AddUser.username)
async def add_user_username(message: Message, state: FSMContext):
    if message.text == "Cancel":
        await state.clear()
        await message.answer("Iptal edildi.")
        return
    await state.update_data(username=message.text)
    await message.answer("Sifre girin:")
    await state.set_state(AddUser.password)

@router.message(AddUser.password)
async def add_user_password(message: Message, state: FSMContext):
    data = await state.get_data()
    success = db.add_user_by_admin(data["username"], message.text)
    if success:
        await message.answer("Kullanici olusturuldu!\n\nKullanici adi: " + data["username"] + "\nSifre: " + message.text)
    else:
        await message.answer("Bu kullanici adi zaten var!")
    await state.clear()

@router.callback_query(F.data == "admin_search_user")
async def cb_search_user(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    users = db.get_all_users()
    if not users:
        await callback.answer("Hic kullanici yok.", show_alert=True)
        return
    try:
        await callback.message.edit_text("Tum Kullanicilar:", reply_markup=kb.users_list_keyboard(users, "detail"))
    except:
        await callback.message.answer("Tum Kullanicilar:", reply_markup=kb.users_list_keyboard(users, "detail"))
    await callback.answer()

@router.callback_query(F.data.startswith("admin_user_"))
async def user_detail(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    user_id = int(callback.data.split("_")[2])
    user = db.get_user_by_id(user_id)
    if not user:
        await callback.answer("Kullanici bulunamadi!", show_alert=True)
        return
    text = (
        "Kullanici Detayi\n\n"
        "ID: " + str(user[0]) + "\n"
        "Kullanici adi: " + str(user[1]) + "\n"
        "Bakiye: " + str(round(user[3], 2)) + "$\n"
        "Kayit: " + str(user[7])
    )
    try:
        await callback.message.edit_text(text, reply_markup=kb.user_detail_keyboard(user_id))
    except:
        await callback.message.answer(text, reply_markup=kb.user_detail_keyboard(user_id))
    await callback.answer()

@router.callback_query(F.data.startswith("delete_user_"))
async def delete_user(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    user_id = int(callback.data.split("_")[2])
    db.delete_user(user_id)
    await callback.answer("Kullanici silindi!", show_alert=True)

@router.callback_query(F.data.startswith("change_pass_"))
async def change_pass(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    user_id = int(callback.data.split("_")[2])
    await state.update_data(user_id=user_id)
    try:
        await callback.message.edit_text("Yeni sifre girin:")
    except:
        await callback.message.answer("Yeni sifre girin:", reply_markup=kb.cancel_keyboard())
    await state.set_state(ChangePassword.password)
    await callback.answer()

@router.message(ChangePassword.password)
async def save_new_password(message: Message, state: FSMContext):
    if message.text == "Cancel":
        await state.clear()
        await message.answer("Iptal edildi.")
        return
    data = await state.get_data()
    db.change_user_password(data["user_id"], message.text)
    await message.answer("Sifre degistirildi: " + message.text)
    await state.clear()

@router.callback_query(F.data.startswith("order_history_"))
async def order_history(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[2])
    orders = db.get_user_orders(user_id)
    if not orders:
        await callback.answer("Satin alim gecmisi yok.", show_alert=True)
        return
    text = "Satin Alim Gecmisi\n\n"
    for o in orders:
        period_text = {"daily": "1 day", "weekly": "7 days", "monthly": "30 days"}.get(o[6], "-")
        text += str(o[3]) + " | " + period_text + " | $" + str(o[5]) + " | " + str(o[7]) + "\n"
    try:
        await callback.message.edit_text(text)
    except:
        await callback.message.answer(text)
    await callback.answer()

@router.callback_query(F.data.startswith("custom_price_"))
async def custom_price_select(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    user_id = int(callback.data.split("_")[2])
    products = db.get_products()
    if not products:
        await callback.answer("Hic urun yok!", show_alert=True)
        return
    try:
        await callback.message.edit_text("Urun secin:", reply_markup=kb.custom_price_products_keyboard(products, user_id))
    except:
        await callback.message.answer("Urun secin:", reply_markup=kb.custom_price_products_keyboard(products, user_id))
    await callback.answer()

@router.callback_query(F.data.startswith("set_custom_"))
async def set_custom_price(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    parts = callback.data.split("_")
    user_id = int(parts[2])
    product_id = int(parts[3])
    await state.update_data(user_id=user_id, product_id=product_id)
    try:
        await callback.message.edit_text("Gunluk ozel fiyat girin:")
    except:
        await callback.message.answer("Gunluk ozel fiyat girin:", reply_markup=kb.cancel_keyboard())
    await state.set_state(CustomPrice.price_daily)
    await callback.answer()

@router.message(CustomPrice.price_daily)
async def save_custom_price_daily(message: Message, state: FSMContext):
    if message.text == "Cancel":
        await state.clear()
        await message.answer("Iptal edildi.")
        return
    await state.update_data(price_daily=message.text.replace(",", "."))
    await message.answer("Haftalik ozel fiyat girin:")
    await state.set_state(CustomPrice.price_weekly)

@router.message(CustomPrice.price_weekly)
async def save_custom_price_weekly(message: Message, state: FSMContext):
    await state.update_data(price_weekly=message.text.replace(",", "."))
    await message.answer("Aylik ozel fiyat girin:")
    await state.set_state(CustomPrice.price_monthly)

@router.message(CustomPrice.price_monthly)
async def save_custom_price_monthly(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        db.set_custom_prices(
            data["user_id"], data["product_id"],
            float(data["price_daily"]),
            float(data["price_weekly"]),
            float(message.text.replace(",", "."))
        )
        await message.answer("Ozel fiyatlar ayarlandi!")
    except Exception as e:
        await message.answer("Hata: " + str(e))
    await state.clear()

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    try:
        await callback.message.edit_text("Istatistikler - Periyot secin:", reply_markup=kb.stats_keyboard())
    except:
        await callback.message.answer("Istatistikler - Periyot secin:", reply_markup=kb.stats_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("stats_"))
async def show_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    if callback.data == "stats_reset":
        conn = sqlite3.connect("/app/data/bot.db")
        c = conn.cursor()
        c.execute("DELETE FROM orders")
        conn.commit()
        conn.close()
        await callback.answer("Istatistikler sifirlandi!", show_alert=True)
        return
    period = callback.data.split("_")[1]
    stats = db.get_stats(period)
    period_text = {"daily": "Gunluk", "weekly": "Haftalik", "monthly": "Aylik"}[period]
    text = (
        period_text + " Istatistikler\n\n"
        "Toplam Satis: " + str(stats["total_orders"]) + " adet\n"
        "Toplam Gelir: $" + str(stats["total_revenue"]) + "\n"
        "Toplam Maliyet: $" + str(stats["total_cost"]) + "\n"
        "Net Kar: $" + str(stats["net_profit"])
    )
    try:
        await callback.message.edit_text(text, reply_markup=kb.stats_keyboard())
    except:
        await callback.message.answer(text, reply_markup=kb.stats_keyboard())
    await callback.answer()

@router.callback_query(F.data == "admin_all_orders")
async def admin_all_orders(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    orders = db.get_all_orders()
    if not orders:
        await callback.answer("Hic siparis yok.", show_alert=True)
        return
    text = "Tum Siparisler\n\n"
    for o in orders:
        period_text = {"daily": "1 day", "weekly": "7 days", "monthly": "30 days"}.get(o[6], "-")
        text += str(o[1]) + " | " + str(o[3]) + " | " + period_text + " | $" + str(o[5]) + " | " + str(o[7]) + "\n"
    try:
        await callback.message.edit_text(text)
    except:
        await callback.message.answer(text)
    await callback.answer()
