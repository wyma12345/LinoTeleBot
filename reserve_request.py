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

    with open('downloaded_files/token.txt') as f:  # заносим предыдущий токен
        api_req_token: str = f.read()
    con = pymysql.connect(host='localhost', user='root', password='root', db='resttelebot')  # подключение к БД

    while True:
        # #sleep(90000)
        # dtime = datetime.date.today()
        # resp = requests.get(
        #     f"https://smartreserve.ru/api/restaurant/rWqOiP5WQTSmEORmZ-Fszw/reservation/export?token={api_req_token}&from={dtime.strftime('%d.%m.%Y')}&to={dtime.strftime('%d.%m.%Y')}")
        # print(resp.status_code)
        # if resp.status_code != 200:  # если нет токена
        #     resp_post = requests.post('https://smartreserve.ru/api/auth', json=DATA_POST)  # аунтифицируемся
        #     api_req_token = resp_post.text  # и присваиваем токен
        #     with open('downloaded_files/token.txt', 'w') as f:  # сохраняем токен в файл
        #         f.write(api_req_token)
        #     continue
        #
        # else:
        #     output = open('downloaded_files/save.xlsx', 'wb')  # открываем файл для сохранения
        #     output.write(resp.content)  # копируем скаченный контент в открытый файл
        #     output.close()
        # sleep(5)
        warnings.simplefilter("ignore")
        data_reserve = pd.read_excel('downloaded_files/save.xlsx', usecols=(1, 3, 4, 5, 7),
                                     engine="openpyxl")  # открываем свой exel

        # with con.cursor() as cur:
        #     for i, row in data_reserve.iterrows():
        #         #print(f"date={row['Дата резерва']}, n_people={row['Кол-во человек']}, telephone={row['Телефон']}, name=row{['Имя']}, table=r{row['Столы']}")
        #         # если нет такого заказа
        #         sql = "SELECT * FROM reserves where date='{}'  and  n_people='{}' and  telephone='{}' and  name='{}';".format(row['Дата резерва'], row['Кол-во человек'], row['Телефон'], row['Имя'])
        #         cur.execute(sql)
        #         if not cur.fetchall():  # если такой заказ уже в БД
        #             # добавляем заказ в БД
        #             sql = "INSERT INTO reserves(date, n_people, telephone, name) VALUES('{}', '{}', '{}', '{}');".format(
        #                 row['Дата резерва'], row['Кол-во человек'], row['Телефон'], row['Имя'])
        #             cur.execute(sql)
        #             # есть ли человек в бд
        #             sql = "SELECT * FROM customers where phone_number='{}';".format(row['Телефон'])  # был ли такой человек ранее
        #             cur.execute(sql)
        #
        #             if not cur.fetchall():  # если таких людей не было
        #                 # добавляем человека в БД
        #                 sql = "INSERT INTO customers(name, phone_number, n_visiting, mailing, reminder, kitchen) VALUES('{}', '{}', '{}', '{}', '{}', '{}');".format(
        #                     row['Имя'], row['Телефон'], 0, 1, 1, 'null')
        #                 cur.execute(sql)
        #             else:  # если такой человек уже был
        #                 # увеличиваем счетчик посещений
        #                 sql = "UPDATE customers SET n_visiting = n_visiting + 1 WHERE phone_number = '{}'".format(row['Телефон'])
        #                 cur.execute(sql)

        # tp = models.Reserves.objects.create(date=row['0'], n_people=row['1'], telephone=row['2'], name=row['3'], table=row['4'])
        save_enter_person(con=con, data_reserve=data_reserve)
        check_time_for_message(con=con)
        con.commit()
        print(data_reserve)

        sleep(multiproc_dict.get('time_loc') * 60)


def save_enter_person(con: pymysql.connect, data_reserve: pd.read_excel):
    with con.cursor() as cur:
        for i, row in data_reserve.iterrows():
            # print(f"date={row['Дата резерва']}, n_people={row['Кол-во человек']}, telephone={row['Телефон']}, name=row{['Имя']}, table=r{row['Столы']}")
            # если нет такого заказа
            date_time_obj = datetime.datetime.strptime(row['Дата резерва'], '%d.%m.%Y %H:%M:%S')
            sql = "SELECT * FROM reserves where date='{}'  and  n_people='{}' and  telephone='{}' and  name='{}';".format(
                date_time_obj, row['Кол-во человек'], row['Телефон'], row['Имя'])
            cur.execute(sql)
            if not cur.fetchall():  # если такой заказ уже в БД
                # добавляем заказ в БД
                sql = "INSERT INTO reserves(date, n_people, telephone, name) VALUES('{}', '{}', '{}', '{}');".format(
                    date_time_obj, row['Кол-во человек'], row['Телефон'], row['Имя'])
                cur.execute(sql)
                # есть ли человек в бд
                sql = "SELECT * FROM customers where phone_number='{}';".format(
                    row['Телефон'])  # был ли такой человек ранее
                cur.execute(sql)

                if not cur.fetchall():  # если таких людей не было
                    # добавляем человека в БД
                    sql = "INSERT INTO customers(name, phone_number, n_visiting, mailing, reminder, kitchen) VALUES('{}', '{}', '{}', '{}', '{}', '{}');".format(
                        row['Имя'], row['Телефон'], 0, 1, 1, 'null')
                    cur.execute(sql)
                else:  # если такой человек уже был
                    # увеличиваем счетчик посещений
                    sql = "UPDATE customers SET n_visiting = n_visiting + 1 WHERE phone_number = '{}'".format(
                        row['Телефон'])
                    cur.execute(sql)


def check_time_for_message(con: pymysql.connect):
    with con.cursor() as cur:
        sql = "SELECT * FROM reserves WHERE date <= NOW() + INTERVAL 40 MINUTE;"
        cur.execute(sql)
    for res in cur.fetchall():
        pass
        ############## добавить отсылку сообщений выбранным пользователям

