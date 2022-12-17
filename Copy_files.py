import os
import shutil


def main():
    months = ['Сентябрь', 'Август']

    with open('loaded_filenames.txt', 'r', encoding='cp1251') as f:
        for month in months:
            for line in f:
                line = line[:-1]
                try:
                    shutil.copy(f'C:\\Users\\user\\Desktop\\Projects\\Kras_Eko-Electro\\data\\{month}\\{line}',
                                f'C:\\Users\\user\\Desktop\\Projects\\Kras_Eko-Electro\\data\\push_{month}\\{line}')
                except FileNotFoundError:
                    print('Не найден')
                print(line)

if __name__ == '__main__':

    main()