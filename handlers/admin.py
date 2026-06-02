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
    price = State()

class AddStock(StatesGroup):
    product_id = State()
    keys = State()

class AddBalance(StatesGroup):
    user_id = State()
    amount = State()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Yetkisiz erişim!")
        return
    await message.answer("👑 Admin Paneli", reply_markup=kb.admin_menu())

@router.message(F.text == "➕ Kategori Ekle")
async def add_category(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Kategori adını girin:")
    await state.set_state(AddCategory.name)

@router.message(AddCategory.name)
async def add_category_name(message: Message, state: FSMContext):
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

@router.message(F.text == "➕ Ürün Ekle")
async def add_product(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    categories = db.get_categories()
    if not categories:
        await message.answer("❌ Önce kategori ekleyin!")
        return
    text = "Kategori ID seçin:\n\n"
    for cat in categories:
        text += f"{cat[0]} - {cat[2]} {cat[1]}\n"
    await message.answer(text)
    await state.set_state(AddProduct.category_id)

@router.message(AddProduct.category_id)
async def add_product_cat(message: Message, state: FSMContext):
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
    await message.answer("Fiyat girin (örn: 10.5):")
    await state.set_state(AddProduct.price)

@router.message(AddProduct.price)
async def add_product_price(message: Message, state: FSMContext):
    data = await state.get_data()
    db.add_product(int(data["category_id"]), data["name"], data["description"], float(message.text))
    await message.answer(f"✅ Ürün eklendi: {data['name']}")
    await state.clear()

@router.message(F.text == "➕ Stok Ekle")
async def add_stock(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    products = db.get_products()
    if not products:
        await message.answer("❌ Önce ürün ekleyin!")
        return
    text = "Ürün ID seçin:\n\n"
    for p in products:
        text += f"{p[0]} - {p[2]}\n"
    await message.answer(text)
    await state.set_state(AddStock.product_id)

@router.message(AddStock.product_id)
async def add_stock_product(message: Message, state: FSMContext):
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

@router.message(F.text == "💰 Bakiye Ekle")
async def add_balance(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Kullanıcı ID girin:")
    await state.set_state(AddBalance.user_id)

@router.message(AddBalance.user_id)
async def add_balance_user(message: Message, state: FSMContext):
    await state.update_data(user_id=message.text)
    await message.answer("Miktar girin (örn: 50):")
    await state.set_state(AddBalance.amount)

@router.message(AddBalance.amount)
async def add_balance_amount(message: Message, state: FSMContext):
    data = await state.get_data()
    db.add_balance(int(data["user_id"]), float(message.text), message.from_user.id)
    await message.answer(f"✅ {message.text} ₺ eklendi!")
    await state.clear()
