import os


def search_file(path: str, extension: str = '.xls') -> list:
    """
    Поиск всех .xls файлов в папке

    :param extension:
    :param path:
    :return:
    """
    list_dir = os.listdir(path)
    xls_list = [i for i in list_dir if extension in i]
    return xls_list
