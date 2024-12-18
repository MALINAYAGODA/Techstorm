import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import asyncio
from main import crawler


TELEGRAM_TOKEN = "6715358280:AAGWw1rZ_0SoVw4K0WI4cr-DQ7lk5y8Ojxs"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Хэндлер на команду /start, /help
@dp.message(Command(commands=["start", "help"]))
async def cmd_start(message: types.Message):
    await message.reply("Привет! Я бот, созданный командой MISIS TRANSFORMERS. Буду рад найти иноформацию в интернете и ответить на ваш вопрос!")

# Хэндлер на получение текстового сообщения
@dp.message(F.text)
async def handle_text(message: types.Message):
    question = message.text
    try:
       response = await crawler(question)
       await message.reply(response)
    except:
       await message.reply("Что-то сломалось - но живем! Задавай вопрос:")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запуск бота
    print("Запуск бота")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
