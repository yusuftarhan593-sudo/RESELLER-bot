from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
import sqlite3
import os
from datetime import datetime

router = Router()
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

class LoginState(StatesGroup):
    username = State()
    password = State()

class BuyMultiple(StatesGroup):
    product_id = State()
    period = State()
    amount = State()

class ResetRequest(StatesGroup):
    key = State()

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    user = db.get_user_by_telegram(message.from_user.id)
    if user:
        await message.answer("👋 Welcome back, " + str(user[1]) + "!", reply_markup=kb.main_menu())
        return
    await message.answer("👋 Welcome!\n\nPlease enter your username:")
    await state.set_state(LoginState.username)

@router.message(LoginState.username)
async def login_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("🔑 Enter your password:")
    await state.set_state(LoginState.password)

@router.message(LoginState.password)
async def login_password(message: Message, state: FSMContext):
    data = await state.get_data()
    user = db.login_user(data["username"], message.text, message.from_user.id)
    if not user:
        await message.answer("❌ Wrong username or password.\n\nEnter your username:")
        await state.set_state(LoginState.username)
        return
    await state.clear()
    await message.answer("✅ Login successful! Welcome, " + str(user[1]) + "!", reply_markup=kb.main_menu())

@router.message(F.text == "🏛️ Account")
async def account(message: Message):
    user = db.get_user_by_telegram(message.from_user.id)
    if not user:
        await message.answer("Please login first. Type /start")
        return
    await message.answer(
        "🏛️ Your Account\n\n👤 Login: " + str(user[1]) + "\n💰 Balance: " + str(round(user[3], 2)) + "$",
        reply_markup=kb.balance_menu_keyboard(user[0])
    )

@router.message(F.text == "🛍️ Buy keys")
async def buy_keys(message: Message):
    user = db.get_user_by_telegram(message.from_user.id)
    if not user:
        await message.answer("Please login first. Type /start")
        return
    categories = db.get_categories()
    if not categories:
        await message.answer("No products available.")
        return
    await message.answer("Select a category:", reply_markup=kb.categories_keyboard(categories))

@router.message(F.text == "🔄 Reset Request")
async def reset_request(message: Message, state: FSMContext):
    user = db.get_user_by_telegram(message.from_user.id)
    if not user:
        await message.answer("Please login first. Type /start")
        return
    await message.answer("🔄 Please enter the key you want to reset:")
    await state.set_state(ResetRequest.key)

@router.message(ResetRequest.key)
async def reset_request_key(message: Message, state: FSMContext):
    user = db.get_user_by_telegram(message.from_user.id)
    key = message.text.strip()
    order = db.get_order_by_key_and_user(key, user[0])
    if not order:
        await message.answer("❌ This key does not belong to you or was not purchased from this bot!")
        await state.clear()
        return
    await state.clear()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    period_text = {"daily": "1 day", "weekly": "7 days", "monthly": "30 days"}.get(order[6], order[6])
    await message.answer("✅ Your reset request has been sent. Please wait for admin approval.")
    await message.bot.send_message(
        ADMIN_ID,
        "🔄 Key Reset Request\n\n"
        "👤 User: " + str(user[1]) + "\n"
        "📦 Product: " + str(order[3]) + "\n"
        "🔑 Key: " + str(key) + "\n"
        "⏱ Period: " + period_text + "\n"
        "📅 Date: " + now,
        reply_markup=kb.reset_request_keyboard(message.from_user.id, user[1])
    )

@router.callback_query(F.data.startswith("reset_approve_"))
async def reset_approve(callback: CallbackQuery):
    user_telegram_id = int(callback.data.split("_")[2])
    await callback.bot.send_message(user_telegram_id, "✅ Your reset request has been approved!")
    await callback.message.edit_text(callback.message.text + "\n\n✅ Approved")
    await callback.answer()

@router.callback_query(F.data.startswith("reset_reject_"))
async def reset_reject(callback: CallbackQuery):
    user_telegram_id = int(callback.data.split("_")[2])
    await callback.bot.send_message(user_telegram_id, "❌ Your reset request has been rejected!")
    await callback.message.edit_text(callback.message.text + "\n\n❌ Rejected")
    await callback.answer()

@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    categories = db.get_categories()
    try:
        await callback.message.edit_text("Select a category:", reply_markup=kb.categories_keyboard(categories))
    except:
        await callback.message.answer("Select a category:", reply_markup=kb.categories_keyboard(categories))
    await callback.answer()

@router.callback_query(F.data.startswith("cat_"))
async def show_products(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    products = db.get_products(category_id)
    if not products:
        await callback.answer("No products in this category.", show_alert=True)
        return
    try:
        await callback.message.edit_text("Select a product:", reply_markup=kb.products_keyboard(products, category_id))
    except:
        await callback.message.answer("Select a product:", reply_markup=kb.products_keyboard(products, category_id))
    await callback.answer()

@router.callback_query(F.data.startswith("product_"))
async def show_product_detail(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = db.get_product(product_id)
    if not product:
        await callback.answer("Product not found!", show_alert=True)
        return
    user = db.get_user_by_telegram(callback.from_user.id)
    custom = db.get_custom_prices(user[0], product_id) if user else None
    price_daily = custom[0] if custom else product[4]
    price_weekly = custom[1] if custom else product[5]
    price_monthly = custom[2] if custom else product[6]
    try:
        await callback.message.edit_text(
            "🗒 Choose a key type for " + str(product[2]) + ":",
            reply_markup=kb.period_select_keyboard(product_id, price_daily, price_weekly, price_monthly)
        )
    except:
        await callback.message.answer(
            "🗒 Choose a key type for " + str(product[2]) + ":",
            reply_markup=kb.period_select_keyboard(product_id, price_daily, price_weekly, price_monthly)
        )
    await callback.answer()

@router.callback_query(F.data.startswith("getfiles_"))
async def get_files(callback: CallbackQuery):
    await callback.message.answer("Get files from our channel: @hilehanemfiles")
    await callback.answer()

@router.callback_query(F.data.startswith("checkstatus_"))
async def check_status(callback: CallbackQuery):
    await callback.answer("Status check coming soon!", show_alert=True)

@router.callback_query(F.data.startswith("period_"))
async def show_period_detail(callback: CallbackQuery):
    parts = callback.data.split("_")
    product_id = int(parts[1])
    period = parts[2]
    user = db.get_user_by_telegram(callback.from_user.id)
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
    stock = db.get_stock_count(product_id, period)
    text = (
        "🔑 " + str(product[2]) + " (" + period_text + ")\n"
        "💰 Price: $" + str(price) + "\n"
        "📦 Stock: " + str(stock) + " keys"
    )
    try:
        await callback.message.edit_text(text, reply_markup=kb.buy_options_keyboard(product_id, period))
    except:
        await callback.message.answer(text, reply_markup=kb.buy_options_keyboard(product_id, period))
    await callback.answer()

@router.callback_query(F.data.startswith("buyone_"))
async def buy_one(callback: CallbackQuery):
    parts = callback.data.split("_")
    product_id = int(parts[1])
    period = parts[2]
    user = db.get_user_by_telegram(callback.from_user.id)
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
    text = (
        "🛒 Confirm Purchase\n\n"
        "🔑 " + str(product[2]) + " x1\n"
        "⏱ " + period_text + "\n"
        "💰 Total: $" + str(price)
    )
    try:
        await callback.message.edit_text(text, reply_markup=kb.confirm_buy_keyboard(product_id, period, 1))
    except:
        await callback.message.answer(text, reply_markup=kb.confirm_buy_keyboard(product_id, period, 1))
    await callback.answer()

@router.callback_query(F.data.startswith("buymulti_"))
async def buy_multiple_ask(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    product_id = int(parts[1])
    period = parts[2]
    await state.update_data(product_id=product_id, period=period)
    await callback.message.answer("How many keys do you want to buy?")
    await state.set_state(BuyMultiple.amount)
    await callback.answer()

@router.message(BuyMultiple.amount)
async def buy_multiple_confirm(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
    except:
        await message.answer("Please enter a valid number!")
        return
    data = await state.get_data()
    product_id = data["product_id"]
    period = data["period"]
    product = db.get_product(product_id)
    user = db.get_user_by_telegram(message.from_user.id)
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
    total = round(price * amount, 2)
    stock = db.get_stock_count(product_id, period)
    if amount > stock:
        await message.answer("❌ Not enough stock! Available: " + str(stock))
        await state.clear()
        return
    await message.answer(
        "🛒 Confirm Purchase\n\n"
        "🔑 " + str(product[2]) + " x" + str(amount) + "\n"
        "⏱ " + period_text + "\n"
        "💰 Total: $" + str(total),
        reply_markup=kb.confirm_buy_keyboard(product_id, period, amount)
    )
    await state.clear()

@router.callback_query(F.data.startswith("confirm_"))
async def do_buy(callback: CallbackQuery):
    user = db.get_user_by_telegram(callback.from_user.id)
    parts = callback.data.split("_")
    product_id = int(parts[1])
    period = parts[2]
    amount = int(parts[3]) if len(parts) > 3 else 1
    keys = []
    for i in range(amount):
        result = db.buy_product(user[0], product_id, period)
        if result is None:
            await callback.message.edit_text("❌ Out of stock!")
            break
        elif result is False:
            await callback.message.edit_text("❌ Insufficient balance!")
            break
        else:
            keys.append(result)
    if keys:
        product = db.get_product(product_id)
        period_text = {"daily": "1 day", "weekly": "7 days", "monthly": "30 days"}.get(period, period)
        text = "✅ Purchase Successful!\n\n🔑 " + str(product[2]) + " (" + period_text + ")\n\n"
        for key in keys:
            text += "`" + str(key) + "`\n"
        await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("order_history_"))
async def order_history_user(callback: CallbackQuery):
    user = db.get_user_by_telegram(callback.from_user.id)
    if not user:
        await callback.answer("Unauthorized!", show_alert=True)
        return
    user_id = int(callback.data.split("_")[2])
    if user[0] != user_id:
        await callback.answer("Unauthorized!", show_alert=True)
        return
    orders = db.get_user_orders(user_id)
    if not orders:
        await callback.message.answer("📋 No purchases yet.")
        await callback.answer()
        return
    text = "📋 Purchase History\n\n"
    for o in orders:
        period_text = {"daily": "1 day", "weekly": "7 days", "monthly": "30 days"}.get(o[6], o[6])
        text += "🔑 " + str(o[3]) + " | " + period_text + " | $" + str(o[5]) + "\n📅 " + str(o[7]) + "\n\n"
    await callback.message.answer(text)
    await callback.answer()

@router.message(F.text == "🚀 Log out")
async def logout(message: Message):
    user = db.get_user_by_telegram(message.from_user.id)
    if user:
        conn = sqlite3.connect("/app/data/bot.db")
        c = conn.cursor()
        c.execute("UPDATE users SET telegram_id=NULL WHERE id=?", (user[0],))
        conn.commit()
        conn.close()
    await message.answer("👋 Logged out. Type /start to login again.", reply_markup=None)
