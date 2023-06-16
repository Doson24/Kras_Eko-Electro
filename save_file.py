import pandas as pd


def save_succes_file(houses: list, file: str):
    """
    Создания списка обработанных файлов

    :param houses: список домов
    :return:
    """
    with open(file, 'w') as f:
        for house in houses:
            f.write(house.path + house.name_file + '\n')


def save_error_file(error_read, file):
    """
    Создания списка НЕ обработанных файлов
    :param error_read:
    :param file:
    :return:
    """
    with open(file, 'w') as f:
        for house in error_read:
            f.write(house + '\n')


def save_summary(db: list):
    """
    Сохранение всех данных в одном файле .Xlsx

    :param db:
    :return:
    """
    for home in db:
        home.entry1['Адресс'] = home.address
    tables = [i.entry1 for i in db]
    sum = pd.concat(tables)
    sum.to_excel('Data.xlsx')

