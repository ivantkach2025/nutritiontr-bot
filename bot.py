
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from datetime import datetime, time
import sqlite3

from config import TOKEN, ADMIN_ID

bot = Bot(token=TOKEN)
dp = Dispatcher()

# База данных
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, date TEXT, report TEXT, photo_id TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS cardio (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, date TEXT, cardio TEXT)''')
conn.commit()

# Команда start
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    if message.from_user.username == ADMIN_ID:
        await message.answer("Привет! Ты админ. Используй /addclient @username чтобы добавить клиента.")
    else:
        await message.answer("Привет! Отправь /report чтобы внести отчёт или /cardio для кардио.")

# Добавление клиента
@dp.message(Command("addclient"))
async def add_client(message: types.Message):
    if message.from_user.username != ADMIN_ID:
        return await message.answer("Только админ может добавлять клиентов.")
    parts = message.text.split()
    if len(parts) == 2 and parts[1].startswith("@"):
        username = parts[1][1:]
        try:
            cursor.execute("INSERT INTO clients (username) VALUES (?)", (username,))
            conn.commit()
            await message.answer(f"Клиент @{username} добавлен.")
        except:
            await message.answer("Клиент уже есть в базе.")
    else:
        await message.answer("Используй: /addclient @username")

# Отчёты
@dp.message(Command("report"))
async def report_cmd(message: types.Message):
    await message.answer("Отправь текст с КБЖУ или фото с описанием.")
    dp.message.register(save_report)

async def save_report(message: types.Message):
    username = message.from_user.username
    date = datetime.now().strftime("%Y-%m-%d")
    text = message.caption or message.text or ""
    photo_id = None
    if message.photo:
        photo_id = message.photo[-1].file_id
    cursor.execute("INSERT INTO reports (username, date, report, photo_id) VALUES (?, ?, ?, ?)", (username, date, text, photo_id))
    conn.commit()
    await message.answer("Отчёт сохранён!")

# Кардио
@dp.message(Command("cardio"))
async def cardio_cmd(message: types.Message):
    await message.answer("Отправь вид кардио и время (например: Бег 30 мин).")
    dp.message.register(save_cardio)

async def save_cardio(message: types.Message):
    username = message.from_user.username
    date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO cardio (username, date, cardio) VALUES (?, ?, ?)", (username, date, message.text))
    conn.commit()
    await message.answer("Кардио добавлено!")

# Статистика
@dp.message(Command("stats"))
async def stats_cmd(message: types.Message):
    if message.from_user.username != ADMIN_ID:
        return await message.answer("Только админ может смотреть статистику.")
    cursor.execute("SELECT username FROM clients")
    clients = cursor.fetchall()
    if not clients:
        return await message.answer("Нет клиентов.")
    text = "Выбери клиента:
" + "\n".join([f"@{c[0]}" for c in clients])
    await message.answer(text)

async def scheduler():
    while True:
        now = datetime.now()
        if now.hour == 18 and now.minute == 0:
            cursor.execute("SELECT username FROM clients")
            for (username,) in cursor.fetchall():
                try:
                    await bot.send_message(f"@{username}", "Напоминание: отправь отчёт за сегодня!")
                except:
                    pass
            await asyncio.sleep(60)
        await asyncio.sleep(30)

async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
