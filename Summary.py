from pympler import summary

from search_file import search_file
import os
from pathlib import Path
from dataclasses import dataclass
import pandas as pd
from bs4 import BeautifulSoup


@dataclass
class Document:
    name: str
    path: str
    type_read: int
    address: str
    summary: list


def detect_type_document(path, filename):
    try:
        pd.read_table(f'{path}/{filename}', encoding='cp1251', decimal=',')
        type_document = 1
    except:
        type_document = None

    if type_document is None:
        try:
            pd.read_excel(f'{path}/{filename}', engine='xlrd', decimal=',')
            type_document = 2
        except:
            type_document = None

    try:
        with open(f'{path}/{filename}') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')
        if soup.body.p.text == 'Эта страница содержит фреймы, однако' \
                               ' текущий браузер их не поддерживает.':
            type_document = 3
    except:
        pass

    return type_document


def search_address(path, name):
    try:
        df = pd.read_table(f'{path}/{name}', encoding='cp1251', decimal=',')
        # Для main_deploy()
        # df = pd.read_table(f'{name}', encoding='cp1251', decimal=',')
        address_row = df[df['Unnamed: 0'].str.startswith('   Адрес').fillna(False)]
        address = address_row.iloc[0][0].strip()[6:]
        type = address.find('Тип')
        address_clear = address[:type].strip()

    except:
        address_clear = None

    if not address_clear:
        try:
            df_xls = pd.read_excel(f'{path}/{name}', engine='xlrd', decimal=',')
            # Чтение xls файлов если не получился прошлый метод
            address = df_xls.iloc[0][0].strip()[7:]
            slice = address.find('\n')
            address_clear = address[:slice]
        except:
            address_clear = None

    return address_clear


def read_tables_type1(path, name):
    df = pd.read_html(f'{path}/{name}', encoding='cp1251', decimal=',')
    return list(df)


def read_tables_type2(path, name):
    df = pd.read_excel(f'{path}/{name}', engine='xlrd', decimal=',')
    return df


def search_summary():
    pass


def main():
    months = ["Июль", "Июнь", 'Август', 'Сентябрь']
    work_dir = str(Path.cwd()) + "\\data\\"
    start_dir = work_dir + 'Сентябрь\\'

    files_names = search_file(start_dir)[:]

    db = []

    for file_name in files_names:
        path = f"{start_dir}{file_name}"
        type_read = detect_type_document(start_dir, file_name)
        address = search_address(start_dir, file_name)

        entries = list()

        if type_read == 1:
            try:
                tables = read_tables_type1(start_dir, file_name)
            except ValueError:
                continue
            count_tables = len(tables)
            # if count_tables == 2:
            try:
                extract_sum_avg(entries, tables)
            except AttributeError:
                continue

        if type_read == 2:
            try:
                tables = read_tables_type2(start_dir, file_name)
            except ValueError:
                continue
            try:
                extract_sum_avg(entries, tables)
            except AttributeError:
                continue

        d1 = Document(name=file_name, path=path, type_read=type_read, address=address, summary=entries)
        db.append(d1)
        print(d1.name, d1.summary)

    print('END')

    count_type3 = [i.type_read == 3 for i in db].count(True)
    name_type3 = [i.name for i in db if i.type_read == 3]

    print(count_type3)


def extract_sum_avg(entries, tables):
    for table in tables:
        columns = table.iloc[0]
        sum_avg = table.iloc[-2:]
        sum_avg.columns = columns
        entries.append(sum_avg)


if __name__ == '__main__':
    main()
