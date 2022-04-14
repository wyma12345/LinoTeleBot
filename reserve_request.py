import datetime
import warnings
from time import sleep
import pandas as pd
import pymysql
import requests
import response
import schedule
import time

DATA_POST = {"login": "Lino", "password": "Lino1+!"}


def reserve_request():
    resp = requests.get(f"//smartreserve.ru/commonpopup/index.html#")
    if resp.status_code == 200:
        return True
    else:
        return False


def check_api_reserve(multiproc_dict):
    """
    Каждые n мин опрашивает сервер если статус плохой, то проводит аунтификацию
    :return: None
    """
    print('start1')
    schedule.every().day.at("06:14").do(every_day_clear_db)
    print('start2')
    with open('downloaded_files/token.txt') as f:  # заносим предыдущий токен
        api_req_token: str = f.read()

    con = pymysql.connect(host='localhost', user='root', password='root', db='resttelebot')  # подключение к БД

    while True:
        sleep(90000)
        dtime = datetime.date.today()
        resp = requests.get(
            f"https://smartreserve.ru/api/restaurant/rWqOiP5WQTSmEORmZ-Fszw/reservation/export?token={api_req_token}&from={dtime.strftime('%d.%m.%Y')}&to={dtime.strftime('%d.%m.%Y')}")
        print(resp.status_code)
        if resp.status_code != 200:  # если нет токена
            resp_post = requests.post('https://smartreserve.ru/api/auth', json=DATA_POST)  # аунтифицируемся
            api_req_token = resp_post.text  # и присваиваем токен
            with open('downloaded_files/token.txt', 'w') as f:  # сохраняем токен в файл
                f.write(api_req_token)
            continue

        else:
            output = open('downloaded_files/save.xlsx', 'wb')  # открываем файл для сохранения
            output.write(resp.content)  # копируем скаченный контент в открытый файл
            output.close()
            sleep(5)
            warnings.simplefilter("ignore")
            data_reserve = pd.read_excel('downloaded_files/save.xlsx', usecols=(1, 3, 4, 5, 7),
                                         engine="openpyxl")  # открываем свой exel
            for i, row in data_reserve.iterrows():
                print(
                    f"date={row['Дата резерва']}, n_people={row['Кол-во человек']}, telephone={row['Телефон']}, name=row{['Имя']}, table=r{row['Столы']}")
                # tp = models.Reserves.objects.create(date=row['0'], n_people=row['1'], telephone=row['2'], name=row['3'], table=row['4'])
            print(data_reserve)

        sleep(multiproc_dict.get('time_loc') * 60)

def every_day_clear_db():
    print('хуй')
