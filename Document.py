from pathlib import Path

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim

from save_file import save_succes_file, save_error_file, save_summary
from search_file import search_file

pd.options.mode.chained_assignment = None


class Document:

    def __init__(self, path, name_file):
        self.path = path            # путь для первого файла, что был найден по адресу
        self.name_file = name_file
        self.type_document = self.detect_type_document()
        # для отображения адреса надо брать из файла

        address_clear = self.search_address()
        if address_clear is None:
            raise TypeError('address is NoneType')
        self.address = self.add_prefix_address(address_clear)

        # locate = self.get_locate()
        # self.longitude = locate[0]
        # self.latitude = locate[1]

        if self.type_document == 1:
            if (len(self.read_tables()) == 4) or (len(self.read_tables()) == 3):
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
        df = pd.read_excel(f'{self.path}/{self.name_file}', engine='xlrd', decimal=',')
        return df

    def clear_data_type2(self, df):
        # 't1/°C', 't2/°C', 'dt/°C', 'V1/м3', 'M1/т', 'V2/м3', 'M2/т', 'Mг/т',
        # 'P1/кг/см2', 'P2/кг/см2', 'Qо/Гкал', 'Qг/Гкал', 'BНP/ч', 'BOC/ч']
        columns = ['Дата/Дата', 'За сутки/См, Гкал', 'M1/т', 'V1/м3', 'M2/т', 'V2/м3', 'dM', 't1/°C', 't2/°C', 'dt/°C',
                   'P1/кг/см2', 'P2/кг/см2', 'Tраб']
        self.entry1 = df.iloc[6:36]
        self.entry2 = df.iloc[55:85]
        drop_n = [2, 8, 9, 10, 11, 12, 16, 17, 18, 20, 22, 23, 25, 26, 27]
        drop_columns1 = [self.entry1.columns[i] for i in drop_n]
        drop_columns2 = [self.entry2.columns[i] for i in drop_n]
        self.entry1.drop(columns=drop_columns1, inplace=True)
        self.entry2.drop(columns=drop_columns2, inplace=True)
        self.entry1.columns = columns
        self.entry2.columns = columns

        self.entry1.index = self.entry1['Дата/Дата']
        self.entry1.drop(columns=['Дата/Дата'], inplace=True)
        self.entry2.index = self.entry2['Дата/Дата']
        self.entry2.drop(columns=['Дата/Дата'], inplace=True)

    def read_tables(self):
        # name = '98лесная4.xls'
        df = pd.read_html(f'{self.path}/{self.name_file}', encoding='cp1251', decimal=',')
        # Для main_deploy()
        # df = pd.read_html(f'{self.name}', encoding='cp1251', decimal=',')
        # df = pd.read_excel(name)
        return list(df)

    def detect_type_document(self):
        try:
            pd.read_table(f'{self.path}/{self.name_file}', encoding='cp1251', decimal=',')
            type_document = 1
        except:
            type_document = None

        if not type_document:
            try:
                pd.read_excel(f'{self.path}/{self.name_file}', engine='xlrd', decimal=',')
                type_document = 2
            except:
                type_document = None

            try:
                with open(f'{self.path}/{self.name_file}') as f:
                    content = f.read()

                soup = BeautifulSoup(content, 'html.parser')
                if soup.body.p.text == 'Эта страница содержит фреймы, однако' \
                                       ' текущий браузер их не поддерживает.':
                    type_document = 3
            except:
                pass

        return type_document

    def search_address(self):
        try:
            df = pd.read_table(f'{self.path}/{self.name_file}', encoding='cp1251', decimal=',')
            # Для main_deploy()
            # df = pd.read_table(f'{self.name}', encoding='cp1251', decimal=',')
            address_row = df[df['Unnamed: 0'].str.startswith('   Адрес').fillna(False)]
            address = address_row.iloc[0][0].strip()[6:]
            type = address.find('Тип')
            address_clear = address[:type].strip()

        except:
            address_clear = None

        if not address_clear:
            try:
                df_xls = pd.read_excel(f'{self.path}/{self.name_file}', engine='xlrd', decimal=',')
                # Чтение xls файлов если не получился прошлый метод
                address = df_xls.iloc[0][0].strip()[7:]
                slice = address.find('\n')
                address_clear = address[:slice]
            except:
                address_clear = None

        return address_clear

    def add_prefix_address(self, address_clear):
        """
        - Поиск адреса в файле
        - добавление префикса к названию

        :return:
        """

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
            return self.name_file
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

    def seach_summary(self):
        pass


if __name__ == '__main__':
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
                # Првоерка на уже существующий дом
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
