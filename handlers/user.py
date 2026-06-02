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
