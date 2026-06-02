from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb

router = Router()

class LoginState(StatesGroup):
    username = State()
    password = State()

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    user = db.get_user_by_telegram(message.from_user.id)
    if user:
        await message.answer(f"Welcome back, {user[1]}! 👋", reply_markup=kb.main_menu())
        return
    await message.answer("👋 Welcome!\n\nPlease enter your username:")
    await state.set_state(LoginState.username)

@router.message(LoginState.username)
async def login_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("🔒 Enter your password:")
    await state.set_state(LoginState.password)

@router.message(LoginState.password)
async def login_password(message: Message, state: FSMContext):
    data = await state.get_data()
    user = db.login_user(data["username"], message.text, message.from_user.id)
    if not user:
        await message.answer("❌ Wrong username or password. Try again.\n\nEnter your username:")
        await state.set_state(LoginState.username)
        return
    await state.clear()
    await message.answer(f"✅ Login successful!\n\nWelcome, {user[1]}! 🎉", reply_markup=kb.main_menu())

@router.message(F.text == "🏦 Account")
async def account(message: Message):
    user = db.get_user_by_telegram(message.from_user.id)
    if not user:
        await message.answer("❌ Please login first. Type /start")
        return
    await message.answer(
        f"👤 *Your account:*\n\n"
        f"- Login: {user[1]}\n"
        f"- Balance: {user[3]}$",
        reply_markup=kb.balance_menu_keyboard(user[0]),
        parse_mode="Markdown"
    )

@router.message(F.text == "🛍️ Buy Keys")
async def buy_keys(message: Message):
    user = db.get_user_by_telegram(message.from_user.id)
    if not user:
        await message.answer("❌ Please login first. Type /start")
        return
    categories = db.get_categories()
    if not categories:
        await message.answer("❌ No products available.")
        return
    await message.answer("🛍️ Select category:", reply_markup=kb.categories_keyboard(categories))

@router.callback_query(F.data.startswith("cat_"))
async def show_products(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    products = db.get_products(category_id)
    if not products:
        await callback.message.answer("❌ No products in this category.")
        await callback.answer()
        return
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("📦 Select product:", reply_markup=kb.products_keyboard(products, category_id))
    await callback.answer()

@router.callback_query(F.data.startswith("product_"))
async def show_product_periods(callback: CallbackQuery):
    user = db.get_user_by_telegram(callback.from_user.id)
    product_id = int(callback.data.split("_")[1])
    product = db.get_product(product_id)
    if not product:
        await callback.answer("❌ Product not found!", show_alert=True)
        return
    custom = db.get_custom_prices(user[0], product_id) if user else None
    price_daily = custom[0] if custom else product[4]
    price_weekly = custom[1] if custom else product[5]
    price_monthly = custom[2] if custom else product[6]
    stock = db.get_stock_count(product_id)
    await callback.message.answer(
        f"🗂 *Choose a key type for {product[2]}:*\n\n📊 Stock: {stock}",
        reply_markup=kb.period_keyboard(product_id, price_daily, price_weekly, price_monthly),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("getfiles_"))
async def get_files(callback: CallbackQuery):
    await callback.answer("📁 Files feature coming soon!", show_alert=True)

@router.callback_query(F.data.startswith("checkstatus_"))
async def check_status(callback: CallbackQuery):
    await callback.answer("🛡 Status check coming soon!", show_alert=True)

@router.callback_query(F.data.startswith("buy_"))
async def confirm_buy(callback: CallbackQuery):
    user = db.get_user_by_telegram(callback.from_user.id)
    parts = callback.data.split("_")
    product_id = int(parts[1])
    period = parts[2]
    product = db.get_product(product_id)
    custom = db.get_custom_prices(user[0], product_id) if user else None
    if period == "daily":
        price = custom[0] if custom else product[4]
        period_text = "1 day"
    elif period == "weekly":
        price = custom[1] if custom else product[5]
        period_text = "7 days"
    else:
        price = custom[2] if custom else product[6]
        period_text = "30 days"
    await callback.message.answer(
        f"✅ *Confirm purchase*\n\n"
        f"📦 {product[2]}\n"
        f"📅 {period_text}\n"
        f"💵 {price}$\n\n"
        f"Confirm?",
        reply_markup=kb.confirm_buy_keyboard(product_id, period),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_"))
async def do_buy(callback: CallbackQuery):
    user = db.get_user_by_telegram(callback.from_user.id)
    parts = callback.data.split("_")
    product_id = int(parts[1])
    period = parts[2]
    result = db.buy_product(user[0], product_id, period)
    if result is None:
        await callback.message.answer("❌ Out of stock!")
    elif result is False:
        await callback.message.answer("❌ Insufficient balance!")
    else:
        await callback.message.answer(f"✅ Purchase successful!\n\n🔑 Key: `{result}`", parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("order_history_"))
async def order_history_user(callback: CallbackQuery):
    user = db.get_user_by_telegram(callback.from_user.id)
    if not user:
        await callback.answer("❌ Unauthorized!", show_alert=True)
        return
    user_id = int(callback.data.split("_")[2])
    if user[0] != user_id:
        await callback.answer("❌ Unauthorized!", show_alert=True)
        return
    orders = db.get_user_orders(user_id)
    if not orders:
        await callback.message.answer("📋 No purchases yet.")
        await callback.answer()
        return
    text = "📋 *Purchase History*\n\n"
    for o in orders:
        period_text = {"daily": "1 day", "weekly": "7 days", "monthly": "30 days"}.get(o[6], o[6])
        text += f"🛍️ {o[3]} | {period_text} | 💵 {o[5]}$ | 📅 {o[7]}\n"
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "back_categories")
async def back_categories(callback: CallbackQuery):
    categories = db.get_categories()
    await callback.message.answer("🛍️ Select category:", reply_markup=kb.categories_keyboard(categories))
    await callback.answer()

@router.message(F.text == "📋 Orders")
async def orders(message: Message):
    user = db.get_user_by_telegram(message.from_user.id)
    if not user:
        await message.answer("❌ Please login first. Type /start")
        return
    orders = db.get_user_orders(user[0])
    if not orders:
        await message.answer("📋 No orders yet.")
        return
    text = "📋 *Your Orders*\n\n"
    for o in orders:
        period_text = {"daily": "1 day", "weekly": "7 days", "monthly": "30 days"}.get(o[6], o[6])
        text += f"🛍️ {o[3]} | {period_text} | 💵 {o[5]}$ | 📅 {o[7]}\n"
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "🚀 Log out")
async def logout(message: Message):
    user = db.get_user_by_telegram(message.from_user.id)
    if user:
        import sqlite3
        conn = sqlite3.connect("bot.db")
        c = conn.cursor()
        c.execute("UPDATE users SET telegram_id=NULL WHERE id=?", (user[0],))
        conn.commit()
        conn.close()
    await message.answer("👋 Logged out successfully. Type /start to login again.", reply_markup=None)
