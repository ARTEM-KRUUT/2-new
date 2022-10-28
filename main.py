import os
import sys
import urllib.request
import zipfile
from pprint import pprint


import requests

URL = "https://pypi.org/simple/"  # Ссылка на pypi


class PackageUnit:
    def __init__(self, name: str):
        self.name = name
        self.dependencies: list[PackageUnit] = []

    def __add__(self, dependency):
        self.dependencies.append(dependency)

    def add(self, dependency):
        self.dependencies.append(dependency)

    def get_name(self):
        return self.name

    def produce_dependency_tree(self):
        res: str = ""
        for dependency in self.dependencies:
            res += "\t" + self.name + " -> " + dependency.name + "\n"
        for dependency in self.dependencies:
            res += dependency.produce_dependency_tree()
        return res


# Функция для нахождения URL для скачивания
def get_url_to_download(content):
    content = content.replace(" ", '\n').split('\n')
    ans = ""
    for i in range(len(content)):
        if ("href=" in content[-1 - i]) and ("whl" in content[-1 - i]):
            ans = content[-1 - i]
            break
    return ans.replace("href=", "")[1:-1]


# Ищим мета данные
def find_meta(dirlist):
    for elem in dirlist:
        if "METADATA" in elem:
            return elem
    return None


# Достаём зависимости
def get_dependencies(lines):
    ans = []
    for elem in lines:
        if ("requires-dist" in elem.lower()) and ("python" not in elem.lower()) and ("extra" not in elem.lower()):
            temp = elem.split()
            for i in range(len(temp)):
                if "requires-dist" in temp[i].lower():
                    ans.append(temp[i + 1])
                    break
    return ans


def main_loop(package_name):
    dependency_unit = PackageUnit(package_name)
    # Делаем запрос на получение ссылки на скачивание пакета
    response = requests.get(URL + package_name + '/')
    url_to_download = get_url_to_download(response.content.decode("UTF-8"))
    # print(url_to_download)
    try:
        # Пробуем скачать пакет
        urllib.request.urlretrieve(url_to_download, package_name + ".zip")
    except ValueError:  # Если скачивание не получается
        print("Package name is invalid")  # Выводим сообщение об ошибке
        sys.exit()  # Заканчиваем выполнение программы

    file = zipfile.ZipFile(package_name + ".zip", 'r')  # Считываем данные из архива
    metadata = file.open(find_meta(file.namelist()), 'r')  # Ищем файл метаданных и открываем его
    text = metadata.readlines()  # Считываем данные
    text = list(i.decode("UTF-8") for i in text)  # Переводим текст в UTF-8

    dependencies = get_dependencies(text)  # Достаём все зависимости
    for dependency in dependencies:
        dependency_unit.add(main_loop(dependency))
        #result[dependency] = main_loop(dependency)

    # Закрываем и удаляем всё, что нужно закрыть и удалить
    metadata.close()
    file.close()
    os.remove(package_name + ".zip")
    return dependency_unit


if __name__ == '__main__':
    n = input("Введите пакет: ")
    res=main_loop(n)
    print("diagraph {\n" + res.produce_dependency_tree() + "}")

