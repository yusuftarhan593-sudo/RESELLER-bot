from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import database as db
import keyboards as kb

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    db.get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )
    await message.answer("Merhaba! Mağazaya hoş geldiniz 🛍", reply_markup=kb.main_menu())

@router.message(F.text == "👤 Hesabım")
async def account(message: Message):
    user = db.get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )
    await message.answer(
        f"👤 *Hesabınız*\n\n"
        f"🆔 ID: `{message.from_user.id}`\n"
        f"💰 Bakiye: {user[3]}₺\n"
        f"📅 Kayıt: {user[6]}",
        parse_mode="Markdown"
    )

@router.message(F.text == "💰 Bakiyem")
async def balance(message: Message):
    user = db.get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )
    await message.answer(
        f"💰 *Bakiyeniz:* {user[3]}₺",
        reply_markup=kb.balance_menu_keyboard(message.from_user.id),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("order_history_"))
async def order_history_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[2])
    if callback.from_user.id != user_id:
        await callback.answer("❌ Yetkisiz!", show_alert=True)
        return
    orders = db.get_user_orders(user_id)
    if not orders:
        await callback.message.answer("📋 Henüz satın alımınız yok.")
        await callback.answer()
        return
    text = "📋 *Satın Alım Geçmişiniz*\n\n"
    for o in orders:
        period_text = {"daily": "Günlük", "weekly": "Haftalık", "monthly": "Aylık"}.get(o[6], o[6])
        text += f"🛍️ {o[3]} | {period_text} | 💵 {o[5]}₺ | 📅 {o[7]}\n"
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@router.message(F.text == "🛍️ Ürünler")
async def products(message: Message):
    categories = db.get_categories()
    if not categories:
        await message.answer("❌ Henüz ürün yok.")
        return
    await message.answer("🛍️ Kategori seçin:", reply_markup=kb.categories_keyboard(categories))

@router.callback_query(F.data.startswith("cat_"))
async def show_products(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    products = db.get_products(category_id)
    if not products:
        await callback.message.answer("❌ Bu kategoride ürün yok.")
        await callback.answer()
        return
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("📦 Ürün seçin:", reply_markup=kb.products_keyboard(products, category_id))
    await callback.answer()

@router.callback_query(F.data.startswith("product_"))
async def show_product_periods(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = db.get_product(product_id)
    if not product:
        await callback.answer("❌ Ürün bulunamadı!", show_alert=True)
        return
    custom = db.get_custom_prices(callback.from_user.id, product_id)
    price_daily = custom[0] if custom else product[4]
    price_weekly = custom[1] if custom else product[5]
    price_monthly = custom[2] if custom else product[6]
    stock = db.get_stock_count(product_id)
    await callback.message.answer(
        f"📦 *{product[2]}*\n\n{product[3]}\n\n📊 Stok: {stock}",
        reply_markup=kb.period_keyboard(product_id, price_daily, price_weekly, price_monthly),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("buy_"))
async def confirm_buy(callback: CallbackQuery):
    parts = callback.data.split("_")
    product_id = int(parts[1])
    period = parts[2]
    product = db.get_product(product_id)
    custom = db.get_custom_prices(callback.from_user.id, product_id)
    if period == "daily":
        price = custom[0] if custom else product[4]
        period_text = "Günlük"
    elif period == "weekly":
        price = custom[1] if custom else product[5]
        period_text = "Haftalık"
    else:
        price = custom[2] if custom else product[6]
        period_text = "Aylık"
    await callback.message.answer(
        f"✅ *Satın alma onayı*\n\n"
        f"📦 {product[2]}\n"
        f"📅 {period_text}\n"
        f"💵 {price}₺\n\n"
        f"Onaylıyor musunuz?",
        reply_markup=kb.confirm_buy_keyboard(product_id, period),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_"))
async def do_buy(callback: CallbackQuery):
    parts = callback.data.split("_")
    product_id = int(parts[1])
    period = parts[2]
    result = db.buy_product(callback.from_user.id, product_id, period)
    if result is None:
        await callback.message.answer("❌ Stok tükendi!")
    elif result is False:
        await callback.message.answer("❌ Yetersiz bakiye!")
    else:
        await callback.message.answer(f"✅ Satın alma başarılı!\n\n🔑 Key: `{result}`", parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "back_categories")
async def back_categories(callback: CallbackQuery):
    categories = db.get_categories()
    await callback.message.answer("🛍️ Kategori seçin:", reply_markup=kb.categories_keyboard(categories))
    await callback.answer()

@router.message(F.text == "📋 Siparişlerim")
async def orders(message: Message):
    orders = db.get_user_orders(message.from_user.id)
    if not orders:
        await message.answer("📋 Henüz siparişiniz yok.")
        return
    text = "📋 *Siparişleriniz*\n\n"
    for o in orders:
        period_text = {"daily": "Günlük", "weekly": "Haftalık", "monthly": "Aylık"}.get(o[6], o[6])
        text += f"🛍️ {o[3]} | {period_text} | 💵 {o[5]}₺ | 📅 {o[7]}\n"
    await message.answer(text, parse_mode="Markdown")
