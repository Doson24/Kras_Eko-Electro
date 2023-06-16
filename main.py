import os

from Document import Document
from save_file import save_succes_file, save_error_file, save_summary
from search_file import search_file

import numpy as np
import pandas as pd
from datetime import date
from geopy.geocoders import Nominatim
import time
from pathlib import Path
from bs4 import BeautifulSoup

pd.options.mode.chained_assignment = None




def uniq_homes():
    """
    Поиск уникальных имен файлов

    :return:
    """
    uniq = []
    months = ['Октябрь', 'Сентябрь', 'Август']
    for month in months:
        data = search_file(f'data/{month}')
        uniq = uniq + data
    return list(set(uniq))


def test_clean(i):
    table = pd.read_html("data_test/Григорьева, 6  ФЛАГМАН.xls", encoding='cp1251', decimal=',')[i]
    columns = table.iloc[0] + '/' + table.iloc[1]
    table.columns = columns

    # Удаляю первые две строки - это название столбцов
    table.drop(index=[0, 1], inplace=True)

    table.index = table[table.columns[0]]
    table.drop(index=[ix for ix in table.index if len(ix) > 9], inplace=True)

    table = table[(table.index != 'Средние:') &
                  (table.index != 'Итого:')
        # (table.index != 'Дата') &
        # (len(table.index) < 10)
                  ]

    table.drop(columns='Дата/Дата', inplace=True)

    # Преобразование к типу Float
    # При чтении использвоать decimal: str = "."
    for column in table.columns:
        try:
            data_column = []
            for i in table[column]:
                if len(i) == 4:
                    data_column.append(i[0:2] + '.' + i[2:4])

                elif len(i) == 3:
                    data_column.append(i[0:1] + '.' + i[1:3])
                elif len(i) == 5:
                    data_column.append(i[0:3] + '.' + i[3:5])
                else:
                    data_column.append(i)

            table[column] = data_column
            table[column] = table[column].astype(float)
        except Exception as ex:
            pass
    #         # print('error')

    # table.index = table.index.astype('datetime64[ns]')
    table.index = pd.to_datetime(table.index, format="%d/%m/%y")

    return table


def main_deploy():
    """
    Для удаленного сервера

    :return:
    """

    # months = ['push_Сентябрь', 'push_Август']
    # work_dir = str(Path.cwd()) + "\\data\\"
    # start_dir = work_dir + 'push_Октябрь\\'

    start_dir = str(Path.cwd())
    files_names = search_file(start_dir)[:10]
    db = []
    error_read = 0
    # Поиск каждого дома по месяцам
    for file_name in files_names:
        path = f"{start_dir}/{file_name}"
        try:
            print(path)
            a1 = Document(start_dir, file_name)
            db.append(a1)
        except (ImportError, KeyError, UnicodeDecodeError):
            print(f'{path} Ошибка открытия: Возможно файл пустой')
            error_read += 1

        # for month in months:
        #     dir_search = work_dir + month
        #     if file_name in search_xls(dir_search):
        #         try:
        #             temp_house = House(dir_search, file_name)
        #             a1.add_entry(temp_house.entry1, temp_house.entry2)
        #
        #         except (ImportError, KeyError, UnicodeDecodeError):
        #             pass
        #             print(f'{dir_search+"/"+file_name} Ошибка открытия: Возможно файл пустой')
        #             error_read += 1

        # print(a1.name)
        # print(a1.entry1)

    # Сохранение имен файлов которые удалось прочитать
    # save_succes_file(db)

    return db, error_read


def main():
    months = [
        "Июль",
        "Июнь",
        'Сентябрь',
        'Октябрь',
    ]
    work_dir = str(Path.cwd()) + "\\data\\"

    db = []
    error_read = []

    # Поиск каждого дома по месяцам
    for month in months:
        path = work_dir + month + '\\'
        files_names = search_file(path)
        for file_name in files_names:
            try:
                doc = Document(path, file_name)
                db_address = [el.address for el in db]
                # Проверка на уже существующий дом
                if doc.address not in db_address:
                    db.append(doc)
                    print(f'{path + file_name} создание')
                # Если уже существует добавляем в уже существующий
                if doc.address in db_address:
                    for num, el_db in enumerate(db):
                        if doc.address == el_db.address:
                            db[num].add_entry(doc.entry1, doc.entry2)
                            print(f'{file_name} добавление в уже существующий')
            except:
                if doc.type_document == 3:
                    empty_file = 'Пустой файл'
                else:
                    empty_file = ''
                print(f'[-]{path + file_name} Ошибка создания документа')
                error_read.append(path + empty_file)

    # Сохранение имен файлов которые удалось прочитать
    save_succes_file(db, 'loaded_filenames.txt')
    save_error_file(error_read, 'error_filenames.txt')
    save_summary(db)

    print('END')

    return db, error_read


if __name__ == '__main__':
    ...
    # '60 лет ВЛКСМ 12'
    # houses, error_read = main()

    # work_dir = str(Path.cwd()) + "\\data\\"
    # print(work_dir)

    # Запуск
    db, error_read = main()
    address = {house.address: i for i, house in enumerate(db)}

    # try:
    #     home = Document('data/Июнь', "90 строительная 7.xls")
    #     # print(home.type_document)
    # except TypeError as ex:
    #     print(ex)
