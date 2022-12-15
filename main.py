import os

import pandas as pd
from datetime import date
pd.options.mode.chained_assignment = None





def search_xls(path: str) -> list:
    list_dir = os.listdir(path)
    xls_list = [i for i in list_dir if '.xls' in i]
    return xls_list


class House:

    def __init__(self, path, name):
        self.path = path
        self.name = name

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
                table[column] = [i[0:2] + '.' + i[2:4] if isinstance(i, str) and len(i) == 4 else i for i in
                                 table[column]]
                table[column] = [i[0:1] + '.' + i[1:3] if isinstance(i, str) and len(i) == 3 else i for i in
                                 table[column]]
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
        # self.entry1.index = self.entry1.sort_index()
        # self.entry2.index = self.entry2.sort_index()

        print('-'*100)


def main():
    months = ['Сентябрь', 'Август']
    work_dir = 'data'
    start_dir = work_dir + '/Октябрь'

    files_names = search_xls(start_dir)[:100]
    db = []

    # Поиск каждого дома по месяцам
    for file_name in files_names:

        try:
            print(f'{start_dir + "/" + file_name}')
            a1 = House(start_dir, file_name)
            db.append(a1)

        except ImportError:
            print(f'{start_dir + "/" + file_name} Ошибка открытия: Возможно файл пустой')

        for month in months:
            dir_search = f'data/{month}'
            if file_name in search_xls(dir_search):
                try:
                    temp_house = House(dir_search, file_name)
                    a1.add_entry(temp_house.entry1, temp_house.entry2)

                except ImportError:
                    pass
                    print(f'{dir_search+"/"+file_name} Ошибка открытия: Возможно файл пустой')
        # print(a1.name)
        # print(a1.entry1)

    return db

def test_clean(i):
    table = pd.read_html("Восточная, 19.xls", encoding='cp1251', decimal=',')[i]
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
            table[column] = [i[0:2] + '.' + i[2:4] if isinstance(i, str) and len(i) == 4 else i for i in
                             table[column]]
            table[column] = [i[0:1] + '.' + i[1:3] if isinstance(i, str) and len(i) == 3 else i for i in
                             table[column]]
            table[column] = table[column].astype(float)
        except Exception as ex:
            pass
    #         # print('error')

    # table.index = table.index.astype('datetime64[ns]')
    table.index = pd.to_datetime(table.index, format="%d/%m/%y")

    return table


if __name__ == '__main__':
    houses = main()
    # for house in houses:
    #     print(house.name)

    # print(test_clean(1))