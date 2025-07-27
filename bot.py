
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN", "8151271225:AAG6-J8nMKn1gxDRN2bChaKCsyTzKTy-CLI")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Бот для отчётов по питанию запущен. Пришли скриншот или напиши КБЖУ.")

@dp.message()
async def receive_report(message: types.Message):
    user = message.from_user.username or message.from_user.full_name
    if message.photo:
        await message.answer(f"Фото отчёта принято от @{user}.")
    else:
        await message.answer(f"Отчёт (КБЖУ) принят от @{user}: {message.text}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
