import os

import numpy as np
import pandas as pd
from datetime import date
from geopy.geocoders import Nominatim
import time
from pathlib import Path

pd.options.mode.chained_assignment = None





def search_xls(path: str) -> list:
    list_dir = os.listdir(path)
    xls_list = [i for i in list_dir if '.xls' in i]
    return xls_list


class House:

    def __init__(self, path, name):
        self.path = path
        self.name = name
        #для отображения адреса надо брать из файла
        self.address = self.read_params()
        locate = self.get_locate()
        self.longitude = locate[0]
        self.latitude = locate[1]

        if len(self.read_tables()) == 4:
            self.entry1 = self.clear_data(self.read_tables()[0])
            self.entry2 = self.clear_data(self.read_tables()[2])

        if len(self.read_tables()) == 2:
            self.entry1 = self.clear_data(self.read_tables()[0])
            self.entry2 = self.clear_data(self.read_tables()[1])

        if len(self.read_tables()) == 1:
            self.entry1 = self.clear_data(self.read_tables()[0])
            self.entry2 = pd.DataFrame(columns=['t1/°C', 'V1/м3', 'M1/т', 'P1/кг/см2',
                                                'Qо/Гкал', 'BНP/ч', 'BOC/ч', None])

    def read_tables(self):
        # name = '98лесная4.xls'
        df = pd.read_html(f'{self.path}/{self.name}', encoding='cp1251', decimal=',')
        # df = pd.read_excel(name)
        return list(df)

    def read_params(self):
        df = pd.read_table(f'{self.path}/{self.name}', encoding='cp1251', decimal=',')
        address_row = df[df['Unnamed: 0'].str.startswith('   Адрес').fillna(False)]
        address = address_row.iloc[0][0].strip()[6:]
        type = address.find('Тип')
        address_clear = address[:type].strip()

        if ' в 1' in address_clear or ' в 2' in address_clear:
            address_clear = address_clear[:-4]

        if 'Ленинградский' in address_clear:
            address_clear = 'проспект ' + address_clear
        elif 'новый путь' in address_clear:
            return address_clear
        else:
            address_clear = 'ул ' + address_clear

        return address_clear
        """
    read_table:
        tb[tb['Unnamed: 0'].str.startswith('Время работы').fillna(False)]

        tb[tb['Unnamed: 0'].str.startswith('Заводской номер').fillna(False)] - надо удалить пробелы вначале каждой ячейки

    read_html:
        df[0][df[0][0]=='Средние:']   
    """

    def clear_data(self, table: pd.DataFrame) -> pd.DataFrame:
        columns = table.iloc[0] + '/' + table.iloc[1]
        table.columns = columns

        # Удаляю первые две строки - это название столбцов
        table.drop(index=[0, 1], inplace=True)
        if np.NaN in table.columns:
            table.drop(np.NaN, axis=1, inplace=True)

        table.index = table[table.columns[0]]
        table.drop(index=[ix for ix in table.index if len(ix) > 9], inplace=True)

        table = table[(table.index != 'Средние:') &
                      (table.index != 'Итого:')
                      # (table.index != 'Дата') &
                      # (len(table.index) < 10)
                  ]

        table.drop(columns='Дата/Дата', inplace=True)

        # Преобразование к типу Float
        # При чтении использвоать decimal: str = "."  - не работает
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

    def add_entry(self, table1: pd.DataFrame, table2: pd.DataFrame):
        self.entry1 = pd.concat([self.entry1, table1])
        self.entry2 = pd.concat([self.entry2, table2])

        # Сортировка по индексу
        self.entry1 = self.entry1.sort_index()
        self.entry2 = self.entry2.sort_index()

        print('-'*100)

    def get_locate(self):
        # [i.split() for i in address]
        print(self.address)
        address = f'ЗАТО Железногорск, {self.address}'
        app = Nominatim(user_agent="tutorial")
        location = app.geocode(address).raw
        latitude = location["lat"]
        longitude = location["lon"]
        return float(latitude), float(longitude)

def save_succeed_filename(houses: list):
    with open('loaded_filenames.txt', 'w') as f:
        for house in houses:
            f.write(house.name + '\n')


def main():
    # months = ['push_Сентябрь', 'push_Август']
    # work_dir = str(Path.cwd()) + "\\data\\"
    # start_dir = work_dir + 'push_Октябрь\\'

    start_dir = str(Path.cwd())
    files_names = search_xls(start_dir)[:100]
    db = []
    error_read = 0
    # Поиск каждого дома по месяцам
    for file_name in files_names:
        path = f"{start_dir}/{file_name}"
        try:
            print(path)
            a1 = House(start_dir, file_name)
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
    save_succeed_filename(db)

    return db, error_read


def uniq_homes():
    uniq = []
    months = ['Октябрь', 'Сентябрь', 'Август']
    for month in months:
        data = search_xls(f'data/{month}')
        uniq = uniq + data
    return list(set(uniq))


def test_clean(i):
    table = pd.read_html("Григорьева, 6  ФЛАГМАН.xls", encoding='cp1251', decimal=',')[i]
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


if __name__ == '__main__':
    # '60 лет ВЛКСМ 12'
    # houses, error_read = main()

    work_dir = str(Path.cwd()) + "\\data\\"
    print(work_dir)
    # address = {house.name: i for i, house in enumerate(houses)}
    # get_locate(address.keys())

    # a = uniq_homes()
    # print(test_clean(0))