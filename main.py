import os

import numpy as np
import pandas as pd
from datetime import date
from geopy.geocoders import Nominatim
import time
from pathlib import Path

pd.options.mode.chained_assignment = None





def search_xls(path: str) -> list:
    """
    Поиск всех .xls файлов в папке

    :param path:
    :return:
    """
    list_dir = os.listdir(path)
    xls_list = [i for i in list_dir if '.xls' in i]
    return xls_list


class House:

    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.type_document = None
        #для отображения адреса надо брать из файла
        self.address = self.add_prefix_address()

        # locate = self.get_locate()
        # self.longitude = locate[0]
        # self.latitude = locate[1]
        if self.type_document == 1:
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
        if self.type_document == 2:
            self.clear_data_type2(self.read_tables_type2())


    def read_tables_type2(self):
        df = pd.read_excel(f'{self.path}/{self.name}', engine='xlrd', decimal=',')
        return df

    def clear_data_type2(self, df):
        # 't1/°C', 't2/°C', 'dt/°C', 'V1/м3', 'M1/т', 'V2/м3', 'M2/т', 'Mг/т',
        # 'P1/кг/см2', 'P2/кг/см2', 'Qо/Гкал', 'Qг/Гкал', 'BНP/ч', 'BOC/ч']
        columns = ['Дата', 'За сутки/См, Гкал', 'M1', 'V1', 'M2', 'V2', 'dM', 't1', 't2', 'dt', 'P1', 'P2', 'Tраб']
        self.entry1 = df.iloc[6:36]
        self.entry2 = df.iloc[55:85]
        drop_n = [2, 8, 9, 10, 11, 12, 16, 17, 18, 20, 22, 23, 25, 26, 27]
        drop_columns1 = [self.entry1.columns[i] for i in drop_n]
        drop_columns2 = [self.entry2.columns[i] for i in drop_n]
        self.entry1.drop(columns=drop_columns1, inplace=True)
        self.entry2.drop(columns=drop_columns2, inplace=True)
        self.entry1.columns = columns
        self.entry2.columns = columns

    def read_tables(self):
        # name = '98лесная4.xls'
        # df = pd.read_html(f'{self.path}/{self.name}', encoding='cp1251', decimal=',')
        # Для main_deploy()
        df = pd.read_html(f'{self.name}', encoding='cp1251', decimal=',')
        # df = pd.read_excel(name)
        return list(df)

    def search_address(self):
        try:
            # df = pd.read_table(f'{self.path}/{self.name}', encoding='cp1251', decimal=',')
            # Для main_deploy()
            df = pd.read_table(f'{self.name}', encoding='cp1251', decimal=',')
            address_row = df[df['Unnamed: 0'].str.startswith('   Адрес').fillna(False)]
            address = address_row.iloc[0][0].strip()[6:]
            type = address.find('Тип')
            address_clear = address[:type].strip()

            self.type_document = 1
        except UnicodeDecodeError:
            df_xls = pd.read_excel(f'{self.path}/{self.name}', engine='xlrd', decimal=',')
            #Чтение xls файлов если не получился прошлый метод
            address = df_xls.iloc[0][0].strip()[7:]
            slice = address.find('\n')
            address_clear = address[:slice]

            self.type_document = 2
        return address_clear

    def add_prefix_address(self):
        """
        - Поиск адреса в файле
        - добавление префикса к названию

        :return:
        """
        address_clear = self.search_address()

        if ' в 1' in address_clear or ' в 2' in address_clear:
            address_clear = address_clear[:-4]

        if 'Ленинградский' in address_clear or 'Курчатова' in address_clear:
            address_clear = 'проспект ' + address_clear
        elif 'новый путь' in address_clear:
            return address_clear
        elif 'Поселковый' in address_clear:
            address_clear = 'проезд ' + address_clear
        elif "проезд" in address_clear or 'пр,' in address_clear:
            return address_clear
        elif '_____________' in address_clear:
            return self.name
        else:
            address_clear = 'ул ' + address_clear
            # return address_clear
        return address_clear
        """
    read_table:
        tb[tb['Unnamed: 0'].str.startswith('Время работы').fillna(False)]

        tb[tb['Unnamed: 0'].str.startswith('Заводской номер').fillna(False)] - надо удалить пробелы вначале каждой ячейки

    read_html:
        df[0][df[0][0]=='Средние:']   
    """

    def clear_data(self, table: pd.DataFrame) -> pd.DataFrame:
        """
        Очистка данных, преобразование в float, тип данных для индекса - Datetime

        :param table:
        :return:
        """
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

        # print('[+] add')

    def get_locate(self):
        # [i.split() for i in address]
        print(self.address)
        address = f'ЗАТО Железногорск, {self.address}'
        app = Nominatim(user_agent="tutorial")
        location = app.geocode(address).raw
        latitude = location["lat"]
        longitude = location["lon"]
        return float(latitude), float(longitude)

def save_succes_file(houses: list, file:str):
    """
    Сохранение имени файлов

    :param houses: список домов
    :return:
    """
    with open(file, 'w') as f:
        for house in houses:
            f.write(house.path + house.name + '\n')


def save_error_file(error_read, file):
    with open(file, 'w') as f:
        for house in error_read:
            f.write(house + '\n')


def uniq_homes():
    """
    Поиск уникальных имен файлов

    :return:
    """
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


def main_deploy():
    """
    Для удаленного сервера

    :return:
    """

    # months = ['push_Сентябрь', 'push_Август']
    # work_dir = str(Path.cwd()) + "\\data\\"
    # start_dir = work_dir + 'push_Октябрь\\'

    start_dir = str(Path.cwd())
    files_names = search_xls(start_dir)[:10]
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
    # save_succes_file(db)

    return db, error_read


def main():
    months = ['Август']
    work_dir = str(Path.cwd()) + "\\data\\"
    start_dir = work_dir + 'Октябрь\\'

    # start_dir = str(Path.cwd())
    files_names = search_xls(start_dir)[:]
    db = []
    error_read = []
    exeptions = (ImportError, KeyError, UnicodeDecodeError, ValueError, IndexError, AttributeError)
    # Поиск каждого дома по месяцам
    for file_name in files_names:
        path = f"{start_dir}{file_name}"
        try:

            a1 = House(start_dir, file_name)
            db.append(a1)
            print(path)
        except exeptions:
            print(f'{path} Ошибка открытия: Возможно файл пустой')
            error_read.append(path)

        for month in months:
            dir_search = work_dir + month + '\\'
            if file_name in search_xls(dir_search):
                try:
                    temp_house = House(dir_search, file_name)
                    a1.add_entry(temp_house.entry1, temp_house.entry2)
                    print(f'{dir_search + file_name}')
                except exeptions:

                    print(f'{dir_search+file_name} Ошибка открытия: Возможно файл пустой')
                    error_read.append(dir_search+file_name)

        # print(a1.name)
        # print(a1.entry1)

    # Сохранение имен файлов которые удалось прочитать
    save_succes_file(db, 'loaded_filenames.txt')
    save_error_file(error_read, 'error_filenames.txt')

    return db, error_read


if __name__ == '__main__':
    # '60 лет ВЛКСМ 12'
    # houses, error_read = main()

    # work_dir = str(Path.cwd()) + "\\data\\"
    # print(work_dir)

    db, error_read = main()
    address = {house.address: i for i, house in enumerate(db)}


