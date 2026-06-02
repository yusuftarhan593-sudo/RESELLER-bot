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

class EditCategory(StatesGroup):
    cat_id = State()
    name = State()
    emoji = State()

class AddProduct(StatesGroup):
    category_id = State()
    name = State()
    description = State()
    price = State()

class EditPrice(StatesGroup):
    product_id = State()
    price = State()

class AddStock(StatesGroup):
    product_id = State()
    keys = State()

class AddBalance(StatesGroup):
    user_id = State()
    amount = State()
    note = State()

class SetDiscount(StatesGroup):
    user_id = State()
    discount = State()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("👑 Admin Paneline Hoş Geldin!", reply_markup=kb.admin_main_menu())

@router.message(F.text == "🔙 Kullanıcı Modu")
async def user_mode(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Kullanıcı moduna geçildi.", reply_markup=kb.main_menu())

@router.message(F.text == "📂 Kategori Yönetimi")
async def category_management(message: Message):
    if not is_admin(message.from_user.id):
        return
    categories = db.get_categories(active_only=False)
    await message.answer("📂 Kategori Yönetimi:", reply_markup=kb.category_manage_keyboard(categories))

@router.callback_query(F.data == "add_category")
async def add_category_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.answer("📂 Yeni kategori adını gir:", reply_markup=kb.cancel_keyboard())
    await state.set_state(AddCategory.name)

@router.message(AddCategory.name)
async def add_category_name(message: Message, state: FSMContext):
    if message.text == "❌ İptal":
        await state.clear()
        await message.answer("İptal edildi.", reply_markup=kb.admin_main_menu())
        return
    await state.update_data(name=message.text)
    await message.answer("Emoji gir (örn: 🎮) veya atlamak için - yaz:")
    await state.set_state(AddCategory.emoji)

@router.message(AddCategory.emoji)
async def add_category_emoji(message: Message, state: FSMContext):
    data = await state.get_data()
    emoji = message.text if message.text != "-" else "📦"
    db.add_category(data["name"], emoji)
    await state.clear()
    await message.answer(f"✅ Kategori eklendi: {emoji} {data['name']}", reply_markup=kb.admin_main_menu())

@router.callback_query(F.data.startswith("del_cat_"))
async def delete_category(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    cat_id = int(callback.data.split("_")[2])
    db.delete_category(cat_id)
    await callback.answer("🗑️ Kategori silindi!", show_alert=True)
    categories = db.get_categories(active_only=False)
    await callback.message.edit_reply_markup(reply_markup=kb.category_manage_keyboard(categories))

@router.callback_query(F.data.startswith("edit_cat_"))
async def edit_category_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    cat_id = int(callback.data.split("_")[2])
    await state.update_data(cat_id=cat_id)
    await callback.message.answer("✏️ Yeni kategori adını gir:", reply_markup=kb.cancel_keyboard())
    await state.set_state(EditCategory.name)

@router.message(EditCategory.name)
async def edit_category_name(message: Message, state: FSMContext):
    if message.text == "❌ İptal":
        await state.clear()
        await message.answer("İptal.", reply_markup=kb.admin_main_menu())
        return
    await state.update_data(name=message.text)
    await message.answer("Emoji gir:")
    await state.set_state(EditCategory.emoji)

@router.message(EditCategory.emoji)
async def edit_category_emoji(message: Message, state: FSMContext):
    data = await state.get_data()
    emoji = message.text if message.text != "-" else "📦"
    db.update_category(data["cat_id"], data["name"], emoji)
    await state.clear()
    await message.answer("✅ Kategori güncellendi!", reply_markup=kb.admin_main_menu())

@router.message(F.text == "📦 Ürün Yönetimi")
async def product_management(message: Message):
    if not is_admin(message.from_user.id):
        return
    products = db.get_all_products_admin()
    await message.answer("📦 Ürün Yönetimi:", reply_markup=kb.product_manage_keyboard(products))

@router.callback_query(F.data == "add_product")
async def add_product_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    categories = db.get_categories()
    if not categories:
        await callback.answer("Önce kategori ekle!", show_alert=True)
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb_inline = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{c[2]} {c[1]}", callback_data=f"select_cat_{c[0]}")] for c in categories])
    await callback.message.answer("Kategori seç:", reply_markup=kb_inline)
    await state.set_state(AddProduct.category_id)

@router.callback_query(F.data.startswith("select_cat_"), AddProduct.category_id)
async def add_product_category(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split("_")[2])
    await state.update_data(category_id=cat_id)
    await callback.message.answer("Ürün adını gir:", reply_markup=kb.cancel_keyboard())
    await state.set_state(AddProduct.name)

@router.message(AddProduct.name)
async def add_product_name(message: Message, state: FSMContext):
    if message.text == "❌ İptal":
        await state.clear()
        await message.answer("İptal.", reply_markup=kb.admin_main_menu())
        return
    await state.update_data(name=message.text)
    await message.answer("Açıklama gir (atlamak için - yaz):")
    await state.set_state(AddProduct.description)

@router.message(AddProduct.description)
async def add_product_desc(message: Message, state: FSMContext):
    desc = message.text if message.text != "-" else ""
    await state.update_data(description=desc)
    await message.answer("Fiyat gir (₺):")
    await state.set_state(AddProduct.price)

@router.message(AddProduct.price)
async def add_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", "."))
    except:
        await message.answer("❌ Geçersiz fiyat! Sayı gir:")
        return
    data = await state.get_data()
    db.add_product(data["category_id"], data["name"], data["description"], price)
    await state.clear()
    await message.answer(f"✅ Ürün eklendi: {data['name']} - {price}₺", reply_markup=kb.admin_main_menu())

@router.callback_query(F.data.startswith("del_product_"))
async def delete_product(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    product_id = int(callback.data.split("_")[2])
    db.delete_product(product_id)
    await callback.answer("🗑️ Ürün silindi!", show_alert=True)
    products = db.get_all_products_admin()
    await callback.message.edit_reply_markup(reply_markup=kb.product_manage_keyboard(products))

@router.callback_query(F.data.startswith("edit_price_"))
async def edit_price_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    product_id = int(callback.data.split("_")[2])
    await state.update_data(product_id=product_id)
    await callback.message.answer("💲 Yeni fiyatı gir (₺):", reply_markup=kb.cancel_keyboard())
    await state.set_state(EditPrice.price)

@router.message(EditPrice.price)
async def edit_price_done(message: Message, state: FSMContext):
    if message.text == "❌ İptal":
        await state.clear()
        await message.answer("İptal.", reply_markup=kb.admin_main_menu())
        return
    try:
        price = float(message.text.replace(",", "."))
    except:
        await message.answer("Geçersiz fiyat:")
        return
    data = await state.get_data()
    db.update_product_price(data["product_id"], price)
    await state.clear()
    await message.answer(f"✅ Fiyat güncellendi: {price}₺", reply_markup=kb.admin_main_menu())

@router.message(F.text == "🔑 Stok Ekle")
async def stock_add_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    products = db.get_all_products_admin()
    if not products:
        await message.answer("Önce ürün ekle!")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb_inline = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{p[2]} (stok: {p[7] if len(p)>7 else 0})", callback_data=f"stock_product_{p[0]}")] for p in products])
    await message.answer("Hangi ürüne stok eklenecek?", reply_markup=kb_inline)
    await state.set_state(AddStock.product_id)

@router.callback_query(F.data.startswith("stock_product_"), AddStock.product_id)
async def stock_select_product(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    await state.update_data(product_id=product_id)
    await callback.message.answer("🔑 Key kodlarını gir (her satıra bir key):", reply_markup=kb.cancel_keyboard())
    await state.set_state(AddStock.keys)

@router.message(AddStock.keys)
async def stock_add_keys(message: Message, state: FSMContext):
    if message.text == "❌ İptal":
        await state.clear()
        await message.answer("İptal.", reply_markup=kb.admin_main_menu())
        return
    data = await state.get_data()
    keys = message.text.strip().split("\n")
    keys = [k.strip() for k in keys if k.strip()]
    db.add_stock(data["product_id"], keys)
    await state.clear()
    await message.answer(f"✅ {len(keys)} adet key eklendi!", reply_markup=kb.admin_main_menu())

@router.message(F.text == "👥 Kullanıcılar")
async def user_management(message: Message):
    if not is_admin(message.from_user.id):
        return
    users = db.get_all_users()
    text = f"👥 <b>Toplam Kullanıcı: {len(users)}</b>\n\n"
    for u in users[:20]:
        status = "⛔" if u[5] == 1 else "✅"
        text += f"{status} <code>{u[0]}</code> | {u[2]} | {u[3]:.2f}₺\n"
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb_inline = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 Bakiye Yükle", callback_data="goto_balance"), InlineKeyboardButton(text="🎁 İndirim Ver", callback_data="goto_discount")],
        [InlineKeyboardButton(text="⛔ Banla", callback_data="goto_ban"), InlineKeyboardButton(text="✅ Ban Kaldır", callback_data="goto_unban")]
    ])
    await message.answer(text, parse_mode="HTML", reply_markup=kb_inline)

@router.message(F.text == "💵 Bakiye Yükle")
async def balance_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Kullanıcı ID'sini gir:", reply_markup=kb.cancel_keyboard())
    await state.set_state(AddBalance.user_id)

@router.callback_query(F.data == "goto_balance")
async def balance_start_cb(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.answer("Kullanıcı ID'sini gir:", reply_markup=kb.cancel_keyboard())
    await state.set_state(AddBalance.user_id)

@router.message(AddBalance.user_id)
async def balance_user_id(message: Message, state: FSMContext):
    if message.text == "❌ İptal":
        await state.clear()
        await message.answer("İptal.", reply_markup=kb.admin_main_menu())
        return
    try:
        uid = int(message.text.strip())
    except:
        await message.answer("Geçersiz ID:")
        return
    user = db.get_user(uid)
    if not user:
        await message.answer("❌ Kullanıcı bulunamadı.")
        return
    await state.update_data(user_id=uid)
    await message.answer(f"Kullanıcı: {user[2]}\nMevcut bakiye: {user[3]:.2f}₺\n\nYüklenecek miktarı gir:")
    await state.set_state(AddBalance.amount)

@router.message(AddBalance.amount)
async def balance_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except:
        await message.answer("Geçersiz miktar:")
        return
    await state.update_data(amount=amount)
    await message.answer("Not ekle (atlamak için - yaz):")
    await state.set_state(AddBalance.note)

@router.message(AddBalance.note)
async def balance_note(message: Message, state: FSMContext):
    data = await state.get_data()
    note = message.text if message.text != "-" else "Admin yüklemesi"
    db.update_balance(data["user_id"], data["amount"])
    db.log_balance(data["user_id"], data["amount"], note, message.from_user.id)
    user = db.get_user(data["user_id"])
    await state.clear()
    await message.answer(f"✅ Bakiye yüklendi!\n\nKullanıcı: {data['user_id']}\nYüklenen: {data['amount']:.2f}₺\nYeni bakiye: {user[3]:.2f}₺", reply_markup=kb.admin_main_menu())

@router.callback_query(F.data == "goto_discount")
async def discount_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.answer("Kullanıcı ID'sini gir:", reply_markup=kb.cancel_keyboard())
    await state.set_state(SetDiscount.user_id)

@router.message(SetDiscount.user_id)
async def discount_user(message: Message, state: FSMContext):
    if message.text == "❌ İptal":
        await state.clear()
        await message.answer("İptal.", reply_markup=kb.admin_main_menu())
        return
    try:
        uid = int(message.text.strip())
    except:
        await message.answer("Geçersiz ID:")
        return
    user = db.get_user(uid)
    if not user:
        await message.answer("Kullanıcı bulunamadı.")
        return
    await state.update_data(user_id=uid)
    await message.answer(f"Kullanıcı: {user[2]}\nMevcut indirim: %{user[4]}\n\nYeni indirim oranı gir (0-100):")
    await state.set_state(SetDiscount.discount)

@router.message(SetDiscount.discount)
async def discount_set(message: Message, state: FSMContext):
    try:
        discount = float(message.text)
        if not 0 <= discount <= 100:
            raise ValueError
    except:
        await message.answer("Geçersiz oran (0-100 arası):")
        return
    data = await state.get_data()
    db.set_custom_discount(data["user_id"], discount)
    await state.clear()
    await message.answer(f"✅ İndirim ayarlandı: %{discount}", reply_markup=kb.admin_main_menu())

@router.message(F.text == "📊 İstatistikler")
async def show_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    total_users, total_orders, total_revenue, total_stock = db.get_stats()
    daily = db.get_earnings("daily")
    weekly = db.get_earnings("weekly")
    monthly = db.get_earnings("monthly")
    yearly = db.get_earnings("yearly")
    text = (f"📊 <b>Genel İstatistikler</b>\n\n"
        f"👥 Toplam Kullanıcı: {total_users}\n"
        f"🛍️ Toplam Sipariş: {total_orders}\n"
        f"💰 Toplam Ciro: {total_revenue:.2f}₺\n"
        f"📦 Toplam Stok: {total_stock}\n\n"
        f"<b>📅 Kazanç Raporu:</b>\n"
        f"• Bugün: {daily[0]:.2f}₺ ({daily[1]} sipariş)\n"
        f"• Bu Hafta: {weekly[0]:.2f}₺ ({weekly[1]} sipariş)\n"
        f"• Bu Ay: {monthly[0]:.2f}₺ ({monthly[1]} sipariş)\n"
        f"• Bu Yıl: {yearly[0]:.2f}₺ ({yearly[1]} sipariş)")
    await message.answer(text, parse_mode="HTML", reply_markup=kb.stats_keyboard())

@router.callback_query(F.data.startswith("stats_"))
async def stats_period(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    period = callback.data.split("_")[1]
    labels = {"daily": "Bugün", "weekly": "Bu Hafta", "monthly": "Bu Ay", "yearly": "Bu Yıl"}
    result = db.get_earnings(period)
    await callback.answer(f"📊 {labels[period]}: {result[0]:.2f}₺ | {result[1]} sipariş", show_alert=True)

@router.message(F.text == "📋 Tüm Siparişler")
async def all_orders(message: Message):
    if not is_admin(message.from_user.id):
        return
    orders = db.get_all_orders()
    if not orders:
        await message.answer("Henüz sipariş yok.")
        return
    text = f"📋 <b>Son Siparişler:</b>\n\n"
    for o in orders[:20]:
        text += f"#{o[0]} | {o[3]} | {o[5]:.2f}₺ | {o[6][:10]}\n"
    await message.answer(text, parse_mode="HTML")
