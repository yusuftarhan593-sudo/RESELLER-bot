from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import database as db
import keyboards as kb

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    user = db.get_or_create_user(
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
        f"👤 Hesabınız\n\n"
        f"🆔 ID: {message.from_user.id}\n"
        f"💰 Bakiye: {user[3]} ₺\n"
        f"📅 Kayıt: {user[6]}"
    )

@router.message(F.text == "💰 Bakiyem")
async def balance(message: Message):
    user = db.get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )
    await message.answer(f"💰 Bakiyeniz: {user[3]} ₺")

@router.message(F.text == "🛍 Ürünler")
async def products(message: Message):
    await message.answer("🛍 Kategoriler yükleniyor...")

@router.message(F.text == "📋 Siparişlerim")
async def orders(message: Message):
    await message.answer("📋 Siparişleriniz yükleniyor...")
