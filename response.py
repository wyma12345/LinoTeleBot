from aiogram import types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from main import dp


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    """
    Возвращает ответ на команду
    :param msg: Сообщение от пользователя
    :return: None
    """
    greet_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    greet_kb.add(KeyboardButton('Резерв'))
    greet_kb.add(KeyboardButton('О боте'))
    await msg.reply(f"Я бот. Приятно познакомиться,{msg.from_user.first_name}", reply_markup=greet_kb)

@dp.message_handler(commands=['help'])
async def send_help(msg: types.Message):
    """
    Возвращает ответ на команду
    :param msg: Сообщение от пользователя
    :return: None
    """
    await msg.reply(f"Тут о работе бота,{msg.from_user.first_name}")