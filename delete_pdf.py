import os
from pathlib import Path

from search_file import search_file


def delete_pdf():
    months = ["Июль", "Июнь", 'Август', 'Сентябрь', 'Октябрь']
    for month in months:
        path = str(Path.cwd()) + "\\data\\" + month + '\\'
        files = search_file(path, '.pdf')
        for file in files:
            os.remove(path + file)


if __name__ == '__main__':
    delete_pdf()