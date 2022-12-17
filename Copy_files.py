import os
import shutil


def main():
    with open('loaded_filenames.txt', 'r', encoding='cp1251') as f:
        for line in f:
            line = line[:-1]
            shutil.copy(f'C:\\Users\\user\\Desktop\\Projects\\Kras_Eko-Electro\\data\\Октябрь\\{line}',
                        f'C:\\Users\\user\\Desktop\\Projects\\Kras_Eko-Electro\\data\\push_Октябрь\\{line}')

            print(line)

if __name__ == '__main__':

    main()