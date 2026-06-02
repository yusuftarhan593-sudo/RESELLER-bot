from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
import os

router = Router()
ADMIN_IDS = [int(os.environ.get("ADMIN_ID", 0))]

def is_admin(user_id):
    return user_id in ADMIN_IDS

class AddCategory(StatesGroup):
    name = State()
    emoji = State()

class AddProduct(StatesGroup):
    category_id = State()
    name = State()
    description = State()
    price_daily = State()
    price_weekly = State()
    price_monthly = State()

class AddStock(StatesGroup):
    product_id = State()
    keys = State()

class AddBalance(StatesGroup):
    user_id = State()
    amount = State()

class SearchUser(StatesGroup):
    user_id = State()

class CustomPrice(StatesGroup):
    user_id = State()
    product_id = State()
    price_daily = State()
    price_weekly = State()
    price_monthly = State()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Yetkisiz erişim!")
        return
    await message.answer(
        "👑 *Admin Paneli*\nNe yapmak istersiniz?",
        reply_markup=kb.admin_inline_menu(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "admin_add_category")
async def cb_add_category(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.answer("Kategori adını girin:", reply_markup=kb.cancel_keyboard())
    await state.set_state(AddCategory.name)
    await callback.answer()

@router.message(AddCategory.name)
async def add_category_name(message: Message, state: FSMContext):
    if message.text == "❌ İptal":
        await state.clear()
        await message.answer("İptal edildi.")
        return
    await state.update_data(name=message.text)
    await message.answer("Emoji girin (opsiyonel, - yazın atlamak için):")
    await state.set_state(AddCategory.emoji)

@router.message(AddCategory.emoji)
async def add_category_emoji(message: Message, state: FSMContext):
    data = await state.get_data()
    emoji = message.text if message.text != "-" else ""
    db.add_category(data["name"], emoji)
    await message.answer(f"✅ Kategori eklendi: {data['name']}")
    await state.clear()

@router.callback_query(F.data == "admin_add_product")
async def cb_add_product(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    categories = db.get_categories()
    if not categories:
        await callback.message.answer("❌ Önce kategori ekleyin!")
        await callback.answer()
        return
    text = "Kategori ID seçin:\n\n"
    for cat in categories:
        text += f"{cat[0]} - {cat[2]} {cat[1]}\n"
    await callback.message.answer(text, reply_markup=kb.cancel_keyboard())
    await state.set_state(AddProduct.category_id)
    await callback.answer()

@router.message(AddProduct.category_id)
async def add_product_cat(message: Message, state: FSMContext):
    if message.text == "❌ İptal":
        await state.clear()
        await message.answer("İptal edildi.")
        return
    await state.update_data(category_id=message.text)
    await message.answer("Ürün adını girin:")
    await state.set_state(AddProduct.name)

@router.message(AddProduct.name)
async def add_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Açıklama girin:")
    await state.set_state(AddProduct.description)

@router.message(AddProduct.description)
async def add_product_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Günlük fiyat girin (örn: 10.5):")
    await state.set_state(AddProduct.price_daily)

@router.message(AddProduct.price_daily)
async def add_product_price_daily(message: Message, state: FSMContext):
    await state.update_data(price_daily=message.text)
    await message.answer("Haftalık fiyat girin (örn: 50):")
    await state.set_state(AddProduct.price_weekly)

@router.message(AddProduct.price_weekly)
async def add_product_price_weekly(message: Message, state: FSMContext):
    await state.update_data(price_weekly=message.text)
    await message.answer("Aylık fiyat girin (örn: 150):")
    await state.set_state(AddProduct.price_monthly)

@router.message(AddProduct.price_monthly)
async def add_product_price_monthly(message: Message, state: FSMContext):
    data = await state.get_data()
    db.add_product(
        int(data["category_id"]), data["name"], data["description"],
        float(data["price_daily"]), float(data["price_weekly"]), float(message.text)
    )
    await message.answer(f"✅ Ürün eklendi: {data['name']}")
    await state.clear()

@router.callback_query(F.data == "admin_add_stock")
async def cb_add_stock(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    products = db.get_products()
    if not products:
        await callback.message.answer("❌ Önce ürün ekleyin!")
        await callback.answer()
        return
    text = "Ürün ID seçin:\n\n"
    for p in products:
        text += f"{p[0]} - {p[2]}\n"
    await callback.message.answer(text, reply_markup=kb.cancel_keyboard())
    await state.set_state(AddStock.product_id)
    await callback.answer()

@router.message(AddStock.product_id)
async def add_stock_product(message: Message, state: FSMContext):
    if message.text == "❌ İptal":
        await state.clear()
        await message.answer("İptal edildi.")
        return
    await state.update_data(product_id=message.text)
    await message.answer("Key/kodları girin (her satıra bir tane):")
    await state.set_state(AddStock.keys)

@router.message(AddStock.keys)
async def add_stock_keys(message: Message, state: FSMContext):
    data = await state.get_data()
    keys = message.text.strip().split("\n")
    for key in keys:
        db.add_stock(int(data["product_id"]), key.strip())
    await message.answer(f"✅ {len(keys)} adet stok eklendi!")
    await state.clear()

@router.callback_query(F.data == "admin_add_balance")
async def cb_add_balance(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.answer("Kullanıcı ID girin:", reply_markup=kb.cancel_keyboard())
    await state.set_state(AddBalance.user_id)
    await callback.answer()

@router.message(AddBalance.user_id)
async def add_balance_user(message: Message, state: FSMContext):
    if message.text == "❌ İptal":
        await state.clear()
        await message.answer("İptal edildi.")
        return
    await state.update_data(user_id=message.text)
    await message.answer("Miktar girin (örn: 50):")
    await state.set_state(AddBalance.amount)

@router.message(AddBalance.amount)
async def add_balance_amount(message: Message, state: FSMContext):
    data = await state.get_data()
    db.add_balance(int(data["user_id"]), float(message.text), message.from_user.id)
    await message.answer(f"✅ {message.text} ₺ eklendi!")
    await state.clear()

@router.callback_query(F.data == "admin_search_user")
async def cb_search_user(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.answer("Kullanıcı ID girin:", reply_markup=kb.cancel_keyboard())
    await state.set_state(SearchUser.user_id)
    await callback.answer()

@router.message(SearchUser.user_id)
async def search_user_result(message: Message, state: FSMContext):
    if message.text == "❌ İptal":
        await state.clear()
        await message.answer("İptal edildi.")
        return
    user_id = int(message.text)
    user = db.get_user(user_id)
    if not user:
        await message.answer("❌ Kullanıcı bulunamadı!")
        await state.clear()
        return
    text = (
        f"👤 *Kullanıcı Bilgileri*\n\n"
        f"🆔 ID: `{user[0]}`\n"
        f"👤 Ad: {user[2]}\n"
        f"💰 Bakiye: {user[3]}₺\n"
    )
    await message.answer(text, reply_markup=kb.user_detail_keyboard(user_id), parse_mode="Markdown")
    await state.clear()

@router.callback_query(F.data.startswith("order_history_"))
async def order_history(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[2])
    orders = db.get_user_orders(user_id)
    if not orders:
        await callback.message.answer("📋 Bu kullanıcının satın alım geçmişi yok.")
        await callback.answer()
        return
    text = f"📋 *Kullanıcı {user_id} - Satın Alım Geçmişi*\n\n"
    for o in orders:
        period_text = {"daily": "Günlük", "weekly": "Haftalık", "monthly": "Aylık"}.get(o[6], "-")
        text += f"🛍️ {o[3]} | {period_text} | 💵 {o[5]}₺ | 📅 {o[7]}\n"
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("custom_price_"))
async def custom_price_select(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    user_id = int(callback.data.split("_")[2])
    products = db.get_products()
    if not products:
        await callback.message.answer("❌ Hiç ürün yok!")
        await callback.answer()
        return
    await callback.message.answer(
        f"👤 Kullanıcı {user_id} için hangi ürüne özel fiyat ayarlamak istersiniz?",
        reply_markup=kb.custom_price_products_keyboard(products, user_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("set_custom_"))
async def set_custom_price(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    parts = callback.data.split("_")
    user_id = int(parts[2])
    product_id = int(parts[3])
    await state.update_data(user_id=user_id, product_id=product_id)
    await callback.message.answer(
        f"💲 Günlük özel fiyat girin:",
        reply_markup=kb.cancel_keyboard()
    )
    await state.set_state(CustomPrice.price_daily)
    await callback.answer()

@router.message(CustomPrice.price_daily)
async def save_custom_price_daily(message: Message, state: FSMContext):
    if message.text == "❌ İptal":
        await state.clear()
        await message.answer("İptal edildi.")
        return
    await state.update_data(price_daily=message.text)
    await message.answer("💲 Haftalık özel fiyat girin:")
    await state.set_state(CustomPrice.price_weekly)

@router.message(CustomPrice.price_weekly)
async def save_custom_price_weekly(message: Message, state: FSMContext):
    await state.update_data(price_weekly=message.text)
    await message.answer("💲 Aylık özel fiyat girin:")
    await state.set_state(CustomPrice.price_monthly)

@router.message(CustomPrice.price_monthly)
async def save_custom_price_monthly(message: Message, state: FSMContext):
    data = await state.get_data()
    db.set_custom_prices(
        data["user_id"], data["product_id"],
        float(data["price_daily"]), float(data["price_weekly"]), float(message.text)
    )
    await message.answer(f"✅ Özel fiyatlar ayarlandı!")
    await state.clear()

@router.message(F.text == "➕ Kategori Ekle")
async def add_category_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Kategori adını girin:", reply_markup=kb.cancel_keyboard())
    await state.set_state(AddCategory.name)

@router.message(F.text == "➕ Ürün Ekle")
async def add_product_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    categories = db.get_categories()
    if not categories:
        await message.answer("❌ Önce kategori ekleyin!")
        return
    text = "Kategori ID seçin:\n\n"
    for cat in categories:
        text += f"{cat[0]} - {cat[2]} {cat[1]}\n"
    await message.answer(text, reply_markup=kb.cancel_keyboard())
    await state.set_state(AddProduct.category_id)

@router.message(F.text == "➕ Stok Ekle")
async def add_stock_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    products = db.get_products()
    if not products:
        await message.answer("❌ Önce ürün ekleyin!")
        return
    text = "Ürün ID seçin:\n\n"
    for p in products:
        text += f"{p[0]} - {p[2]}\n"
    await message.answer(text, reply_markup=kb.cancel_keyboard())
    await state.set_state(AddStock.product_id)

@router.message(F.text == "💰 Bakiye Ekle")
async def add_balance_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Kullanıcı ID girin:", reply_markup=kb.cancel_keyboard())
    await state.set_state(AddBalance.user_id)
