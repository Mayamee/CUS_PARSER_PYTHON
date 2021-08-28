import re
import json
from datetime import datetime


class CUSParser(object):
    """
    Парсер CUS, применяется для разбора логов
    """

    def __init__(self, pattern):
        """
        Constructor записывает паттерн и инициализирует внутреннее поле для приема данных
        """
        self.rgxString = pattern
        self.parsed = False
        self.data = ""

    def setData(self, data):
        """
        Записывает данные в объект
        :param data: String
        :return: Self for chaining
        """
        self.data = data
        self.parsed = False
        return self

    def toDict(self, listElem):
        """
        Ручная функция применяется для парсинга списка в словарь
        :param listElem: list или tuple
        :return: Dict
        """
        return {
            "Уровень": listElem[0],
            "Дата и время": listElem[1],
            "Источник": listElem[2],
            "Код события": int(listElem[3]),
            "Категория задачи": listElem[4],
            "Описание": listElem[5]
        }

    def toDictSec(self, listElem):
        """
        Ручная функция применяется для парсинга списка в словарь
        :param listElem: list или tuple
        :return: Dict
        """
        return {
            "Уровень": listElem[0],
            "Дата и время": listElem[1],
            "Источник": listElem[2],
            "Код события": int(listElem[3]),
            "Категория задачи": listElem[4],
            "Описание": " ".join(listElem[5:])
        }

    def compress(self):
        """
        Сжимает строку с одну для регулярного выражения
        :return: Self for chaining
        """
        self.data = re.sub("(\n|\r)", "", self.data)
        return self

    def repairString(self):
        """
        Решение проблем коллизий для регулярного выражения
        :return: Self for chaining
        """
        self.data = re.sub("(Ошибка|Сведения|Предупреждение)[ :]", "Error ", self.data)
        return self

    def parse(self):
        """
        Парсит файл
        :return: Self for chaining
        """
        self.data = re.findall(self.rgxString, self.data)
        self.data = map(lambda item: item[1].split("\t"), self.data)
        self.data = list(map(self.toDict, self.data))
        self.parsed = True
        return self

    def parseSec(self):
        """
        Парсит файл SEC
        :return: Self for chaining
        """
        self.data = re.findall(self.rgxString, self.data)
        self.data = map(lambda item: item[1].split("\t"), self.data)
        self.data = list(map(self.toDictSec, self.data))
        self.parsed = True
        return self

    def getData(self):
        """
        Достает данные из объекта
        :return: List of Dicts
        """
        return self.data

    def sortByDate(self):
        """
        Сортировка по дате
        :return: Self for chaining
        """
        if self.parsed:
            self.data.sort(key=lambda item: datetime.strptime(item["Дата и время"], "%d.%m.%Y %H:%M:%S"))
            return self
        else:
            raise Exception("Данные не распаршены нечего сортировать")


class FileManager(object):
    """
    Работает с файлами и папками
    """

    # диман л0х почухаю пузико
    def __init__(self):
        """
        Constructor filesystem module
        """
        pass

    def loadData(self, name):
        """
        Читает сырые данные из файла для парсинга
        :return: None
        """
        with open(name, "r", encoding="utf-8") as file:
            return str(file.read())

    def writeData(self, name, data):
        """
        Записывает данные в файл
        :return: None
        """
        with open(name, "w", encoding="utf-8") as file:
            file.write(data)

    def toJSON(self, variable):
        """
        Преобразует данные в формат JSON
        :return: JSON formatted string
        """
        return json.dumps(variable, indent=2, ensure_ascii=False)


regPattern = \
    {
        'APP': "(?=(Сведения|Ошибка|Предупреждение))(.+?)(?=(Сведения|Ошибка|Предупреждение))",
        'SECURITY': "(?=(Аудит успеха))(.+?)(?=(Аудит успеха))",
        'SYSTEM': "(?=(Сведения|Ошибка|Предупреждение))(.+?)(?=(Сведения|Ошибка|Предупреждение))",
    }


def main():
    FM = FileManager()
    parserApp = CUSParser(regPattern["APP"])
    parserSec = CUSParser(regPattern["SECURITY"])
    parserSys = CUSParser(regPattern["SYSTEM"])

    try:
        dataApp = FM.loadData("app.txt") + "Сведения"
        resultApp = parserApp.setData(dataApp).repairString().compress().parse().sortByDate().getData()
        jsonDataApp = FM.toJSON(resultApp)
        FM.writeData("app.json", jsonDataApp)
    except:
        print("Не удалось обработать файл app.txt")

    try:
        dataSec = FM.loadData("security.txt") + "Аудит успеха"
        resultSec = parserSec.setData(dataSec).compress().parseSec().sortByDate().getData()
        jsonDataSec = FM.toJSON(resultSec)
        FM.writeData("security.json", jsonDataSec)
    except:
        print("Не удалось обработать файл security.txt")

    try:
        dataSys = FM.loadData("system.txt") + "Сведения"
        resultSys = parserSys.setData(dataSys).repairString().compress().parse().sortByDate().getData()
        jsonDataSys = FM.toJSON(resultSys)
        FM.writeData("system.json", jsonDataSys)
    except:
        print("Не удалось обработать файл system.txt")


main()
