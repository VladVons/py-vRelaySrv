import os
import aiogram
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = os.getenv('Env_TelegramToken')
print(API_TOKEN)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


#------------------------Блок обработки входящих сообщений------------------------------
@dp.message_handler(commands=['start']) #Приветствие
async def echo(message: types.Message):
    await message.answer('''Здравствуйте Вы подключились к боту . Чтобы узнать возможности Бота введите команду /help''')

@dp.message_handler(commands=['help']) #Помощь
async def echo(message: types.Message):
    await message.answer('help')

@dp.message_handler(commands=['add']) #Функция добавления фильтра
async def echo(message: types.Message):
    await message.answer('add')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
