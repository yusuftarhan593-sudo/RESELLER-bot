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

@router.callback_query(F.data == "admin_add_category")
async def cb_add_category(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
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

@router.callback_query(F.data == "admin_add_product")
async def cb_add_product(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    categories = db.get_categories()
    if not categories:
        await callback.message.answer("Once kategori ekleyin!")
        await callback.answer()
        return
    text = "Kategori ID secin:\n\n"
    for cat in categories:
        text += str(cat[0]) + " - " + str(cat[2]) + " " + str(cat[1]) + "\n"
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
    await state.update_data(price_daily=message.text.replace(",", "."))
    await message.answer("Haftalik satis fiyati girin:")
    await state.set_state(AddProduct.price_weekly)

@router.message(AddProduct.price_weekly)
async def add_product_price_weekly(message: Message, state: FSMContext):
    await state.update_data(price_weekly=message.text.replace(",", "."))
    await message.answer("Aylik satis fiyati girin:")
    await state.set_state(AddProduct.price_monthly)

@router.message(AddProduct.price_monthly)
async def add_product_price_monthly(message: Message, state: FSMContext):
    await state.update_data(price_monthly=message.text.replace(",", "."))
    await message.answer("Gunluk MALIYET girin:")
    await state.set_state(AddProduct.cost_daily)

@router.message(AddProduct.cost_daily)
async def add_product_cost_daily(message: Message, state: FSMContext):
    await state.update_data(cost_daily=message.text.replace(",", "."))
    await message.answer("Haftalik MALIYET girin:")
    await state.set_state(AddProduct.cost_weekly)

@router.message(AddProduct.cost_weekly)
async def add_product_cost_weekly(message: Message, state: FSMContext):
    await state.update_data(cost_weekly=message.text.replace(",", "."))
    await message.answer("Aylik MALIYET girin:")
    await state.set_state(AddProduct.cost_monthly)

@router.message(AddProduct.cost_monthly)
async def add_product_cost_monthly(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        db.add_product(
            int(data["category_id"]), data["name"], data["description"],
            float(data["price_daily"]), float(data["price_weekly"]), float(data["price_monthly"]),
            float(data["cost_daily"]), float(data["cost_weekly"]), float(message.text.replace(",", "."))
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
        await callback.message.answer("Once urun ekleyin!")
        await callback.answer()
        return
    text = "Urun ID secin:\n\n"
    for p in products:
        text += str(p[0]) + " - " + str(p[2]) + "\n"
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

@router.callback_query(F.data.startswith("stock_period_"))
async def stock_period_select(callback: CallbackQuery, state: FSMContext):
    period = callback.data.split("_")[2]
    await state.update_data(period=period)
    period_text = {"daily": "1 Gun", "weekly": "7 Gun", "monthly": "30 Gun"}[period]
    await callback.message.answer("Periyot: " + period_text + "\
