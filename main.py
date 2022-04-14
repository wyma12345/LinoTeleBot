import datetime
import warnings
from time import sleep

import pandas as pd
import phonenumbers
from dateutil.relativedelta import relativedelta
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from multiprocessing import Process
import requests
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from threading import Thread
import multiprocessing
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import pymysql
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import response
from reserve_request import check_api_reserve
# con = pymysql.connect('localhost', 'root', 'root', 'resttelebot')  # подключение к бд


# class BotStates(Helper):
#     mode = HelperMode.snake_case
#
#     RESERVE_STATE_NUMBER = ListItem()  # это [4]
#     RESERVE_STATE_TIME = ListItem()  # это [3]
#     RESERVE_STATE_N_PEOPLE = ListItem()  # это [2]
#     RESERVE_STATE_NAME = ListItem()  # это [1]
#     RESERVE_STATE_DOP_INFO = ListItem()  # это [0]


TOKEN = "5253025565:AAGNOnQrYih_8_1k4DY4nEgziaEhwX7zymQ"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# time_loc: int = 30  # задержка опроса
api_req_token = 'eyJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..bLKch2X1S1qUYHVOKfIqeQ.Npv5Na1rrH1cVgsgkAYSbKk7IhIb29gXYncIn6nf2TwLH1c65v9YSlvBs_vbfzVTVSMpGixaDLwGlr4XnZbuPmmqulYBfZ2LW8e3UGIJm0QJTtpCsKz1aNcdmEfxoFUdfrHFwg-PIXlEgfDFR8qoAvy5lJJXnZevIwSEcL5-Xl5uY7LtyPtQ2wjQgkgZAeK6A0J5C6ALcRJ7J9bIDvW2hLMH5jgxSo7pfD5XbAy8FKrUPPAOxvQQ7U4J9TkSy80Ia0XGPrAmjwdy77lzwfh5lUtWtaGpEfD389sQKTXOKand8CKw8btQoUAnpultKY5Q.QeraTGvXEf2VWtQOXvG9BQ'
DATA_POST = {"login": "Lino", "password": "Lino1+!"}


def main(multiproc_dict: dict):
    """
    Запускает процесс опроса сервера и опроса на скачку
    :return: None
    """
    # proc = Process(target=check_api_reserve)
    # proc.start()
    thread1 = Thread(target=check_api_reserve, args=(multiproc_dict,))
    thread1.start()
    executor.start_polling(dp)


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


reserv_info: dict = {'date': '', 'n_people': '', 'number': '', 'name': '', 'dop_info': ''}


@dp.message_handler(content_types=['text'])
async def send_help(msg: types.Message):
    """
    Обработка сообщений
    :param msg: Сообщение от пользователя
    :return: None
    """
    greet_kb = ReplyKeyboardMarkup(resize_keyboard=True)

    if msg.text.lower() == 'о боте':
        # greet_kb.one_time_keyboard = True
        greet_kb.add(KeyboardButton('Резерв'))
        await msg.reply(f"Тут о работе бота,{msg.from_user.first_name}", reply_markup=greet_kb)
    elif msg.text.lower() == 'резерв':
        # state = dp.current_state(user=msg.from_user.id)
        # greet_kb.add(KeyboardButton('Отмена'))
        # await state.set_state('reserve_state_time')

        await msg.answer(f"Тут сообщение, что нет брони, но можно пользоваться телефоном (телефон)", reply_markup=greet_kb)
        # хм, тут надо собрать доступное время и дать выбор(или узнать как робит кнопка с кодом)
    # elif msg.text.lower() == 'отмена':
    #     await send_welcome(msg)


# @dp.message_handler(content_types=['text'], state=BotStates.RESERVE_STATE_TIME)
# async def send_reserve_time(msg: types.Message):
#     if msg.text.lower() == 'отмена':
#         state = dp.current_state(user=msg.from_user.id)
#         await state.reset_state()
#         await send_welcome(msg)
#         return
#
#     try:
#         date_time_obj = datetime.datetime.strptime(f'{msg.text.lower()}.{datetime.date.today().year}', f'%d.%m.%Y')
#         reserv_info['date'] = date_time_obj.strftime('%Y.%m.%d')
#         state = dp.current_state(user=msg.from_user.id)
#         await state.set_state('reserve_state_n_people')
#         await msg.answer(f"Укажите количество персон")
#     except ValueError:
#         await msg.answer(f"Неверный формат даты, пожалуйста, попробуйте снова")
#
#
# @dp.message_handler(content_types=['text'], state=BotStates.RESERVE_STATE_N_PEOPLE)
# async def send_reserve_n_people(msg: types.Message):
#     if msg.text.lower() == 'отмена':
#         state = dp.current_state(user=msg.from_user.id)
#         await state.reset_state()
#         await send_welcome(msg)
#         return
#
#     try:
#         if int(msg.text) < 1:
#             raise ValueError
#         reserv_info['n_people'] = str(int(msg.text))
#         state = dp.current_state(user=msg.from_user.id)
#         await state.set_state('reserve_state_number')
#         # greet_kb = ReplyKeyboardMarkup(resize_keyboard=True)
#         # greet_kb.add(KeyboardButton('Взять номер телеграмма'))
#         # greet_kb.add(KeyboardButton('Ввести другой номер'))
#         # greet_kb.add(KeyboardButton('Отмена'))
#         await msg.answer(f"Укажите номер")
#     except ValueError:
#         await msg.answer(f"Неверный ввод, пожалуйста, попробуйте снова")
#
#
# @dp.message_handler(content_types=['text'], state=BotStates.RESERVE_STATE_NUMBER)
# async def send_reserve_number(msg: types.Message):
#     if msg.text.lower() == 'отмена':
#         state = dp.current_state(user=msg.from_user.id)
#         await state.reset_state()
#         await send_welcome(msg)
#         return
#
#     if msg.text[0] == '8':
#         msg.text = '+7' + msg.text.replace('8', '', 1)
#
#     try:
#         my_number = phonenumbers.parse(msg.text)
#         if phonenumbers.is_valid_number(my_number):
#             reserv_info['number'] = msg.text
#             state = dp.current_state(user=msg.from_user.id)
#             await state.set_state('reserve_state_name')
#             greet_kb = ReplyKeyboardMarkup(resize_keyboard=True)
#             greet_kb.add(KeyboardButton(
#                 f'Использовать {msg.from_user.last_name if msg.from_user.last_name is not None else ""} {msg.from_user.first_name if msg.from_user.first_name is not None else ""}'))
#             greet_kb.add(KeyboardButton('Отмена'))
#             await msg.answer(f"Укажите фамилию и/или имя", reply_markup=greet_kb)
#         else:
#             await msg.answer(f"Неверный ввод, пожалуйста, попробуйте снова")
#     except phonenumbers.phonenumberutil.NumberParseException:
#         await msg.answer(f"Неверный ввод, пожалуйста, попробуйте снова")
#         reserv_info['name'] = msg.text
#
#
# @dp.message_handler(content_types=['text'], state=BotStates.RESERVE_STATE_NAME)
# async def send_reserve_name(msg: types.Message):
#     if msg.text.lower() == 'отмена':
#         state = dp.current_state(user=msg.from_user.id)
#         await state.reset_state()
#         await send_welcome(msg)
#         return
#
#     if msg.text.split()[0] == f'Использовать':
#         reserv_info[
#             'name'] = f'{msg.from_user.last_name if msg.from_user.last_name is not None else ""} {msg.from_user.first_name if msg.from_user.first_name is not None else ""}'
#     else:
#         reserv_info['name'] = msg.text
#     state = dp.current_state(user=msg.from_user.id)
#     await state.set_state('reserve_state_dop_info')
#     greet_kb = ReplyKeyboardMarkup(resize_keyboard=True)
#     greet_kb.add(KeyboardButton('Да'))
#     greet_kb.add(KeyboardButton('Нет'))
#     greet_kb.add(KeyboardButton('Отмена'))
#     await msg.answer(f"Хотите ввести доп сведения?", reply_markup=greet_kb)
#
#
# @dp.message_handler(content_types=['text'], state=BotStates.RESERVE_STATE_DOP_INFO)
# async def send_reserve_dop_info(msg: types.Message):
#     if msg.text.lower() == 'отмена':
#         state = dp.current_state(user=msg.from_user.id)
#         await state.reset_state()
#         await send_welcome(msg)
#         return
#
#     if msg.text.lower() == 'нет':
#         state = dp.current_state(user=msg.from_user.id)
#         await state.reset_state()
#
#         if reserve_request:
#             await msg.answer("Стол забронирован!")
#         else:
#             await msg.answer("Ошибка")
#
#         await send_welcome(msg)
#     # if msg.text.lower() == 'да':
#     #     await msg.answer("Вводите:")
#     elif msg.text.lower() != 'да':
#         reserv_info['dop_info'] = msg.text.lower()
#         state = dp.current_state(user=msg.from_user.id)
#         await state.reset_state()
#
#         if reserve_request:
#             await msg.answer("Стол забронирован!")
#         else:
#             await msg.answer("Ошибка")
#
#         await send_welcome(msg)
#     print(reserv_info)


# def reserve_request():
#     resp = requests.get(f"//smartreserve.ru/commonpopup/index.html#")
#     if resp.status_code == 200:
#         return True
#     else:
#         return False
#
#
# def check_api_reserve(multiproc_dict):
#     """
#     Каждые n мин опрашивает сервер если статус плохой, то проводит аунтификацию
#     :return: None
#     """
#     global api_req_token
#     while True:
#         sleep(90000)
#         dtime = datetime.date.today()
#         resp = requests.get(
#             # f"https://smartreserve.ru/api/restaurant/rWqOiP5WQTSmEORmZ-Fszw/reservation/export?token={api_req_token}&from={(dtime - relativedelta(months=multiproc_dict.get('month_delay'))).strftime('%d.%m.%Y')}&to={dtime.strftime('%d.%m.%Y')}")
#             f"https://smartreserve.ru/api/restaurant/rWqOiP5WQTSmEORmZ-Fszw/reservation/export?token={api_req_token}&from={dtime.strftime('%d.%m.%Y')}&to={dtime.strftime('%d.%m.%Y')}")
#         print(resp.status_code)
#         if resp.status_code != 200:  # если нет токена
#             resp_post = requests.post('https://smartreserve.ru/api/auth', json=DATA_POST)  # аунтифицируемся
#             api_req_token = resp_post.text  # и присваиваем токен
#             continue
#         else:
#             # print(api_req_token)
#             output = open('downloaded_files/save.xlsx', 'wb')  # открываем файл для сохранения
#             output.write(resp.content)  # копируем скаченный контент в открытый файл
#             output.close()
#             sleep(5)
#             warnings.simplefilter("ignore")
#             data_reserve = pd.read_excel('downloaded_files/save.xlsx', usecols=(1, 3, 4, 5, 7),
#                                          engine="openpyxl")  # открываем свой exel
#             for i, row in data_reserve.iterrows():
#                 print(
#                     f"date={row['Дата резерва']}, n_people={row['Кол-во человек']}, telephone={row['Телефон']}, name=row{['Имя']}, table=r{row['Столы']}")
#                 # tp = models.Reserves.objects.create(date=row['0'], n_people=row['1'], telephone=row['2'], name=row['3'], table=row['4'])
#             print(data_reserve)
#
#         sleep(multiproc_dict.get('time_loc') * 60)


if __name__ == '__main__':
    main({'time_loc': 15, 'month_delay': 1})
