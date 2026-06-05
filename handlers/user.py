from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
import sqlite3

router = Router()

class LoginState(StatesGroup):
    username = State()
    password = State()

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    user = db.get_user_by_telegram(message.from_user.id)
    if user:
        await message.answer("Welcome back, " + str(user[1]) + "!", reply_markup=kb.main_menu())
        return
    await message.answer("Welcome!\n\nPlease enter your username:")
    await state.set_state(LoginState.username)

@router.message(LoginState.username)
async def login_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Enter your password:")
    await state.set_state(LoginState.password)

@router.message(LoginState.password)
async def login_password(message: Message, state: FSMContext):
    data = await state.get_data()
    user = db.login_user(data["username"], message.text, message.from_user.id)
    if not user:
        await message.answer("Wrong username or password. Try again.\n\nEnter your username:")
        await state.set_state(LoginState.username)
        return
    await state.clear()
    await message.answer("Login successful! Welcome, " + str(user[1]) + "!", reply_markup=kb.main_menu())

@router.message(F.text == "🏛️ Account")
async def account(message: Message):
    user = db.get_user_by_telegram(message.from_user.id)
    if not user:
        await message.answer("Please login first. Type /start")
        return
    await message.answer(
        "Your account:\n\n- Login: " + str(user[1]) + "\n- Balance: " + str(user[3]) + "$",
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
    await message.answer("Select category:", reply_markup=kb.categories_keyboard(categories))

@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    categories = db.get_categories()
    try:
        await callback.message.edit_text("Select category:", reply_markup=kb.categories_keyboard(categories))
    except:
        await callback.message.answer("Select category:", reply_markup=kb.categories_keyboard(categories))
    await callback.answer()

@router.callback_query(F.data == "back_categories")
async def back_categories(callback: CallbackQuery):
    categories = db.get_categories()
    try:
        await callback.message.edit_text("Select category:", reply_markup=kb.categories_keyboard(categories))
    except:
        await callback.message.answer("Select category:", reply_markup=kb.categories_keyboard(categories))
    await callback.answer()

@router.callback_query(F.data.startswith("cat_"))
async def show_products(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    products = db.get_products(category_id)
    if not products:
        await callback.answer("No products in this category.", show_alert=True)
        return
    try:
        await callback.message.edit_text("Select product:", reply_markup=kb.products_keyboard(products, category_id))
    except:
        await callback.message.answer("Select product:", reply_markup=kb.products_keyboard(products, category_id))
    await callback.answer()

@router.callback_query(F.data.startswith("product_"))
async def show_product_periods(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = db.get_product(product_id)
    if not product:
        await callback.answer("Product not found!", show_alert=True)
        return
    try:
        await callback.message.edit_text(
            "Choose a key type for " + str(product[2]) + ":",
            reply_markup=kb.period_select_keyboard(product_id)
        )
    except:
        await callback.message.answer(
            "Choose a key type for " + str(product[2]) + ":",
            reply_markup=kb.period_select_keyboard(product_id)
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
    cat = db.get_category_by_id(product[1])
    cat_name = cat[1] if cat else "-"
    text = (
        "🔑 Key " + str(product[2]) + " (" + period_text + "):\n"
        "- Category: " + cat_name + "\n"
        "- Price: " + str(price) + "$\n"
        "- Keys in stock: " + str(stock)
    )
    try:
        await callback.message.edit_text(text, reply_markup=kb.buy_detail_keyboard(product_id, period))
    except:
        await callback.message.answer(text, reply_markup=kb.buy_detail_keyboard(product_id, period))
    await callback.answer()

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
            await callback.message.answer("Out of stock!")
            break
        elif result is False:
            await callback.message.answer("Insufficient balance!")
            break
        else:
            keys.append(result)
    if keys:
        product = db.get_product(product_id)
        period_text = {"daily": "1 day", "weekly": "7 days", "monthly": "30 days"}.get(period, period)
        text = "🔑 Your key " + str(product[2]) + " (" + period_text + ") :\n"
        for key in keys:
            text += "`" + str(key) + "`\n"
        await callback.message.answer(text, parse_mode="Markdown")
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
        await callback.message.answer("No purchases yet.")
        await callback.answer()
        return
    text = "Purchase History\n\n"
    for o in orders:
        period_text = {"daily": "1 day", "weekly": "7 days", "monthly": "30 days"}.get(o[6], o[6])
        text += str(o[3]) + " | " + period_text + " | $" + str(o[5]) + " | " + str(o[7]) + "\n"
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
    await message.answer("Logged out. Type /start to login again.", reply_markup=None)
