import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import os

from database import init_db
from handlers import admin, user

logging.basicConfig(level=logging.INFO)

async def main():
    init_db()
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(admin.router)
    dp.include_router(user.router)
    print("Bot başlatıldı!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
